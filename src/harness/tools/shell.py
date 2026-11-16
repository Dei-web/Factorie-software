from pathlib import Path

import strands_shell


def create_project_shell(workdir: Path):
    workdir = workdir.resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    return strands_shell.Shell(
        binds=[
            strands_shell.Bind(
                str(workdir),
                "/workspace",
                mode="direct",
            )
        ],
        timeout=60.0,
        limits=strands_shell.Limits(
            max_output=1 << 20,
            max_file_size=10 << 20,
        ),
    )
