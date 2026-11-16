from typing import Protocol

from harness.domain.state import TaskResult


class TaskInputPort(Protocol):
    def submit(self, description: str, conversation_key: str = ...) -> TaskResult: ...

    def reset(self, conversation_key: str = ...) -> None: ...
