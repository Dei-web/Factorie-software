from harness.aplication.services.submit_task import SubmitTask

CLI_CONVERSATION = "cli"


def run_cli() -> None:
    submit_task = SubmitTask()

    print("Factorie-Ia CLI")
    print("Escribe '/nuevo' para empezar una conversación nueva o 'exit' para salir.\n")

    while True:
        try:
            description = input("Factorie> ").strip()

            if not description:
                continue

            if description.lower() in {"exit", "quit"}:
                break

            if description.lower() in {"/nuevo", "/new"}:
                submit_task.reset(CLI_CONVERSATION)
                print("Conversación reiniciada.\n")
                continue

            result = submit_task.submit(description, CLI_CONVERSATION)

            while True:
                print("\n--- RESULTADO ---")
                print(f"Execution ID: {result.execution_id}")

                if not result.interrupted:
                    print(result.response)
                    break

                print("\nEl agente necesita información:")
                print(result.response)

                user_response = input("\nTu respuesta: ").strip()

                if not user_response:
                    print("Debes proporcionar una respuesta.")
                    continue

                result = submit_task.resume(
                    execution_id=result.execution_id,
                    interrupt_id=result.interrupt_id,
                    response=user_response,
                )

        except KeyboardInterrupt:
            print("\nSaliendo de Factorie-Ia...")
            break

        except Exception as error:
            print(f"\nError al procesar la tarea: {error}")
