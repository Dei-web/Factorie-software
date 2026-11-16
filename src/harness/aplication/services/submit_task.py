from strands.vended_tools.handoff_to_user import HANDOFF_INTERRUPT_NAME

from harness.domain.state import TaskResult
from harness.factorie import create_application, memory_manager

DEFAULT_PROJECT = "telegram_project"


class SubmitTask:
    """Envía tareas al agente manteniendo una conversación continua por ``conversation_key``.

    Cada clave (p. ej. ``"cli"`` o ``"telegram:<chat_id>"``) conserva su historial entre
    mensajes y entre reinicios del proceso, hasta que se llama a :meth:`reset`.
    """

    def __init__(self, project_name: str = DEFAULT_PROJECT):
        self.project_name = project_name
        # conversation_key -> {"agent", "execution"} (caché en proceso).
        self.conversations = {}
        # execution_id -> conversation_key, para ejecuciones esperando respuesta del usuario.
        self.pending_executions = {}

    def _get_conversation(self, conversation_key: str):
        conversation = self.conversations.get(conversation_key)

        if conversation is None:
            agent, workdir, execution, is_new = create_application(
                project_name=self.project_name,
                conversation_key=conversation_key,
            )
            conversation = {
                "agent": agent,
                "workdir": workdir,
                "execution": execution,
                "is_new": is_new,
            }
            self.conversations[conversation_key] = conversation

        return conversation

    def submit(self, description: str, conversation_key: str = "cli") -> TaskResult:
        conversation = self._get_conversation(conversation_key)
        agent = conversation["agent"]
        execution = conversation["execution"]

        # El contexto del proyecto solo hace falta al inicio; los mensajes siguientes
        # llegan tal cual, como en una conversación normal.
        if conversation["is_new"] and not agent.messages:
            prompt = (
                f"EXECUTION_ID: {execution.execution_id}\n"
                f"WORKDIR: {conversation['workdir']}\n\n"
                f"TAREA:\n{description}"
            )
        else:
            prompt = description
        conversation["is_new"] = False

        result = agent(prompt)
        return self._process_result(result, conversation_key)

    def resume(
        self,
        execution_id: str,
        interrupt_id: str,
        response: str,
    ) -> TaskResult:
        conversation_key = self.pending_executions.get(execution_id)

        if conversation_key is None or conversation_key not in self.conversations:
            raise ValueError("No existe una ejecución pendiente.")

        agent = self.conversations[conversation_key]["agent"]
        result = agent(
            [
                {
                    "interruptResponse": {
                        "interruptId": interrupt_id,
                        "response": response,
                    }
                }
            ]
        )

        return self._process_result(result, conversation_key)

    def reset(self, conversation_key: str = "cli") -> None:
        """Olvida la conversación: el próximo mensaje empieza una sesión nueva."""
        conversation = self.conversations.pop(conversation_key, None)

        if conversation is not None:
            self.pending_executions.pop(conversation["execution"].execution_id, None)

        memory_manager.reset_conversation(conversation_key)

    def _process_result(self, result, conversation_key: str) -> TaskResult:
        execution = self.conversations[conversation_key]["execution"]

        handoff = next(
            (
                interrupt
                for interrupt in (result.interrupts or [])
                if interrupt.name == HANDOFF_INTERRUPT_NAME
            ),
            None,
        )

        if result.stop_reason == "interrupt" and handoff:
            self.pending_executions[execution.execution_id] = conversation_key

            return TaskResult(
                execution_id=execution.execution_id,
                response=handoff.reason,
                interrupted=True,
                interrupt_id=handoff.id,
            )

        self.pending_executions.pop(execution.execution_id, None)

        return TaskResult(
            execution_id=execution.execution_id,
            response=str(result),
        )
