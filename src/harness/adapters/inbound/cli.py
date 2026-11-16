from harness.aplication.services.submit_task import SubmitTask

CLI_CONVERSATION = "cli"


def run_cli() -> None:
    submit_task = SubmitTask()

    print("Factorie-Ia CLI")
    print("Comandos: /nuevo (conversación y proyecto nuevos), /proyecto <nombre>")
    print("(trabajar en un proyecto existente de generated_projects/), exit para salir.")
    print("Cada conversación nueva crea su propia carpeta de proyecto.\n")

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

            if description.lower().startswith("/proyecto"):
                name = description[len("/proyecto"):].strip()
                if not name:
                    print(f"Proyecto actual: {submit_task.current_project(CLI_CONVERSATION)}\n")
                    continue
                name = submit_task.select_project(name, CLI_CONVERSATION)
                print(f"Siguiente tarea en generated_projects/{name}\n")
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
