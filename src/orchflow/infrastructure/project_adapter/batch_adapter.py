"""Windows batch-file lifecycle adapter for OrchFlow."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime

from orchflow.application.lifecycle import LifecycleOrchestrationError, ProjectLifecycleAdapter
from orchflow.domain.lifecycle import LifecycleExecutionResult
from orchflow.domain.project_registry import CanonicalLifecycleAction, Project


@dataclass(frozen=True, slots=True)
class WindowsBatchProjectAdapter(ProjectLifecycleAdapter):
    """Executes lifecycle actions through a Windows `.bat` command-dispatch contract."""

    timeout_seconds: int = 120

    def execute(
        self,
        project: Project,
        action: CanonicalLifecycleAction,
    ) -> LifecycleExecutionResult:
        if sys.platform != "win32":
            raise LifecycleOrchestrationError(
                "Windows batch lifecycle execution is only supported on Windows."
            )

        command_identifier = self._resolve_command_identifier(project, action)
        command = [
            "cmd.exe",
            "/c",
            "call",
            project.lifecycle_script_path,
            command_identifier,
        ]
        started_at = datetime.now(UTC)
        completed = subprocess.run(
            command,
            cwd=project.project_root_path,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        finished_at = datetime.now(UTC)
        return LifecycleExecutionResult(
            project_id=project.id,
            canonical_action=action,
            command_identifier=command_identifier,
            exit_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
            succeeded=completed.returncode == 0,
            started_at=started_at,
            finished_at=finished_at,
        )

    @staticmethod
    def _resolve_command_identifier(project: Project, action: CanonicalLifecycleAction) -> str:
        for mapping in project.action_mappings:
            if mapping.canonical_action is action:
                return mapping.script_label
        return action.value.upper()
