"""Authenticated, local-only Windows path selection workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from orchflow.domain.access_control import User

PathSelectionKind = Literal["project_root", "lifecycle_script"]


class LocalPathSelectionError(Exception):
    """Raised when local path selection cannot be completed safely."""


class CurrentUserResolver(Protocol):
    def get_current_user(self, token: str) -> User: ...


class AuditRecorder(Protocol):
    def record_audit_event(
        self,
        *,
        actor_user_id: int,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class LocalPathSelectionResult:
    status: Literal["selected", "cancelled"]
    path: str | None = None


class LocalPathSelectionService:
    def __init__(
        self,
        *,
        current_user_resolver: CurrentUserResolver,
        audit_recorder: AuditRecorder,
        api_host: str,
    ) -> None:
        self._current_user_resolver = current_user_resolver
        self._audit_recorder = audit_recorder
        self._api_host = api_host.lower()

    def select_path(self, *, token: str, kind: PathSelectionKind) -> LocalPathSelectionResult:
        actor = self._current_user_resolver.get_current_user(token)
        if self._api_host not in {"localhost", "127.0.0.1", "::1"}:
            self._record(actor, kind, "rejected")
            raise LocalPathSelectionError(
                "Local path selection is available only from a local API host."
            )
        try:
            selected = self._choose_path(kind)
        except Exception as error:
            self._record(actor, kind, "failed")
            raise LocalPathSelectionError(
                "The local Windows path dialog could not be opened."
            ) from error
        if not selected:
            self._record(actor, kind, "cancelled")
            return LocalPathSelectionResult(status="cancelled")
        path = Path(selected)
        valid = path.is_absolute() and (
            (kind == "project_root" and path.is_dir())
            or (kind == "lifecycle_script" and path.is_file() and path.suffix.lower() == ".bat")
        )
        if not valid:
            self._record(actor, kind, "rejected")
            raise LocalPathSelectionError("The selected path is not valid for this field.")
        self._record(actor, kind, "selected")
        return LocalPathSelectionResult(status="selected", path=str(path))

    def _record(self, actor: User, kind: PathSelectionKind, outcome: str) -> None:
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="local_path_selection",
            target_type="local_path",
            target_id=None,
            details=f"kind:{kind};outcome:{outcome}",
        )

    @staticmethod
    def _choose_path(kind: PathSelectionKind) -> str:
        import tkinter
        from tkinter import filedialog

        root = tkinter.Tk()
        root.withdraw()
        try:
            return (
                filedialog.askdirectory(title="Select project folder")
                if kind == "project_root"
                else filedialog.askopenfilename(
                    title="Select lifecycle script", filetypes=[("Batch files", "*.bat")]
                )
            )
        finally:
            root.destroy()
