import asyncio
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from harness.aplication.services.submit_task import SubmitTask
from harness.domain.state import TaskRequest

load_dotenv()

submit_task = SubmitTask()

# chat_id -> ejecución e interrupción pendiente.
pending_chats = {}


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message:
        await update.message.reply_text("Factorie-Ia conectada.\nEnvíame una tarea.")


async def new_conversation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat_id = update.effective_chat.id
    pending_chats.pop(chat_id, None)
    submit_task.reset(f"telegram:{chat_id}")

    if update.message:
        await update.message.reply_text("Conversación reiniciada. Envíame una tarea nueva.")


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    message = update.message.text.strip()

    try:
        pending = pending_chats.get(chat_id)

        if pending:
            result = await asyncio.to_thread(
                submit_task.resume,
                execution_id=pending["execution_id"],
                interrupt_id=pending["interrupt_id"],
                response=message,
            )
        else:
            request = TaskRequest(
                description=message,
                source="telegram",
            )

            result = await asyncio.to_thread(
                submit_task.submit,
                request.description,
                f"telegram:{chat_id}",
            )

        if result.interrupted:
            pending_chats[chat_id] = {
                "execution_id": result.execution_id,
                "interrupt_id": result.interrupt_id,
            }

            response_text = (
                "🤖 Factorie-Ia necesita información:\n\n"
                f"{result.response}\n\n"
                "Responde a este mensaje para continuar."
            )

        else:
            pending_chats.pop(chat_id, None)

            response_text = f"✅ Ejecución finalizada:\n\n{result.response}"

        await update.message.reply_text(response_text)

    except Exception:
        await update.message.reply_text("No pude procesar la tarea. Revisa los logs.")
        raise


def run_telegram_bot() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuevo", new_conversation))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("Factorie-Ia escuchando mensajes de Telegram...")
    app.run_polling()
