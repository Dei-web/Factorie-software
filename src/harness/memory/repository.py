import sqlite3
from pathlib import Path

from harness.memory.memories import ExecutionMemory


class MemoryRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_key TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def save(self, execution: ExecutionMemory):
        execution.updated_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO executions (
                    execution_id,
                    project_name,
                    status,
                    data,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(execution_id)
                DO UPDATE SET
                    status = excluded.status,
                    data = excluded.data,
                    updated_at = excluded.updated_at
            """,
                (
                    execution.execution_id,
                    execution.project_name,
                    "running",
                    execution.model_dump_json(),
                    execution.updated_at.isoformat(),
                ),
            )

    def get(self, execution_id: str):
        with self._connect() as connection:
            row = connection.execute(
                "SELECT data FROM executions WHERE execution_id = ?", (execution_id,)
            ).fetchone()

        if row is None:
            return None

        return ExecutionMemory.model_validate_json(row["data"])

    def get_conversation(self, conversation_key: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT execution_id FROM conversations WHERE conversation_key = ?",
                (conversation_key,),
            ).fetchone()

        return None if row is None else row["execution_id"]

    def set_conversation(self, conversation_key: str, execution_id: str):
        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations (conversation_key, execution_id, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(conversation_key)
                DO UPDATE SET
                    execution_id = excluded.execution_id,
                    updated_at = excluded.updated_at
            """,
                (conversation_key, execution_id, now.isoformat()),
            )

    def delete_conversation(self, conversation_key: str):
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM conversations WHERE conversation_key = ?",
                (conversation_key,),
            )
