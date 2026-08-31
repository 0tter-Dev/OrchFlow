"""Windows runtime inspection helpers for OrchFlow."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from orchflow.application.runtime_inspection import RuntimeInspectionError, RuntimeInspector
from orchflow.domain.project_registry import Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot, RuntimeProcessSnapshot

APP_PORT_PATTERN = re.compile(r'APP_PORT=(?P<port>\d+)')
APP_URL_PATTERN = re.compile(r'APP_URL=(?P<url>[^\r\n"]+)')
DOTNET_JSON_DATE_PATTERN = re.compile(r"^/Date\((?P<milliseconds>-?\d+)\)/$")


@dataclass(frozen=True, slots=True)
class ApplicationReachabilityCheck:
    """Result of checking the optional application URL."""

    reachable: bool | None
    detail: str | None


@dataclass(frozen=True, slots=True)
class WindowsRuntimeInspector(RuntimeInspector):
    """Inspects ports and process metadata for Windows-first managed projects."""

    powershell_executable: str = "powershell"
    reachability_timeout_seconds: float = 1.5

    def inspect(self, project: Project) -> RuntimeInspectionSnapshot:
        inspected_at = datetime.now(UTC)
        known_port, application_url = self._extract_script_runtime_hints(
            project.lifecycle_script_path
        )
        reachability = self._check_application_reachability(application_url)
        if sys.platform != "win32":
            return RuntimeInspectionSnapshot(
                project_id=project.id,
                status="unsupported",
                status_reason="Runtime inspection is currently implemented for Windows only.",
                known_port=known_port,
                application_url=application_url,
                application_reachable=reachability.reachable,
                uptime_seconds=None,
                process_snapshots=(),
                inspected_at=inspected_at,
            )

        pids = self._find_port_pids(known_port) if known_port is not None else []
        processes = self._load_process_snapshots(pids)
        uptime_seconds = None
        if processes:
            started_values = [
                process.started_at
                for process in processes
                if process.started_at is not None
            ]
            if started_values:
                oldest_start = min(started_values)
                uptime_seconds = (inspected_at - oldest_start).total_seconds()
        status = self._derive_status(
            known_port=known_port,
            process_count=len(processes),
            application_url=application_url,
            application_reachable=reachability.reachable,
        )
        status_reason = self._build_status_reason(
            status=status,
            known_port=known_port,
            application_url=application_url,
            application_reachable=reachability.reachable,
            reachability_detail=reachability.detail,
            process_count=len(processes),
        )
        return RuntimeInspectionSnapshot(
            project_id=project.id,
            status=status,
            status_reason=status_reason,
            known_port=known_port,
            application_url=application_url,
            application_reachable=reachability.reachable,
            uptime_seconds=uptime_seconds,
            process_snapshots=tuple(processes),
            inspected_at=inspected_at,
        )

    @staticmethod
    def _extract_script_runtime_hints(lifecycle_script_path: str) -> tuple[int | None, str | None]:
        content = Path(lifecycle_script_path).read_text(encoding="utf-8", errors="ignore")
        port_match = APP_PORT_PATTERN.search(content)
        url_match = APP_URL_PATTERN.search(content)
        port = int(port_match.group("port")) if port_match else None
        application_url = url_match.group("url").strip() if url_match else None
        return port, application_url

    @staticmethod
    def _find_port_pids(port: int) -> list[int]:
        completed = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeInspectionError("Unable to inspect netstat output.")

        pids: list[int] = []
        needle = f":{port}"
        for line in completed.stdout.splitlines():
            if needle not in line or "LISTENING" not in line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                pid = int(parts[-1])
            except ValueError:
                continue
            if pid not in pids:
                pids.append(pid)
        return pids

    def _check_application_reachability(
        self,
        application_url: str | None,
    ) -> ApplicationReachabilityCheck:
        if application_url is None:
            return ApplicationReachabilityCheck(reachable=None, detail=None)

        request = Request(application_url, method="GET")
        try:
            with urlopen(request, timeout=self.reachability_timeout_seconds):
                return ApplicationReachabilityCheck(reachable=True, detail="responded")
        except HTTPError:
            return ApplicationReachabilityCheck(reachable=True, detail="responded with HTTP error")
        except TimeoutError:
            return ApplicationReachabilityCheck(
                reachable=False,
                detail=f"timed out after {self.reachability_timeout_seconds:g}s",
            )
        except URLError as error:
            reason = error.reason
            if isinstance(reason, TimeoutError):
                return ApplicationReachabilityCheck(
                    reachable=False,
                    detail=f"timed out after {self.reachability_timeout_seconds:g}s",
                )
            return ApplicationReachabilityCheck(
                reachable=False,
                detail=f"failed reachability check: {reason}",
            )
        except (OSError, ValueError) as error:
            return ApplicationReachabilityCheck(
                reachable=False,
                detail=f"failed reachability check: {error}",
            )

    @staticmethod
    def _derive_status(
        *,
        known_port: int | None,
        process_count: int,
        application_url: str | None,
        application_reachable: bool | None,
    ) -> str:
        if process_count > 0:
            return "running"
        if known_port is None and application_url is None:
            return "unsupported"
        if known_port is None and application_reachable:
            return "running"
        return "stopped"

    @staticmethod
    def _build_status_reason(
        *,
        status: str,
        known_port: int | None,
        application_url: str | None,
        application_reachable: bool | None,
        reachability_detail: str | None,
        process_count: int,
    ) -> str:
        if known_port is None:
            if application_url is not None and application_reachable:
                return (
                    "No APP_PORT hint was found in the lifecycle script, but APP_URL "
                    f"{application_url} {reachability_detail or 'responded'}."
                )
            if application_url is not None:
                return (
                    "No APP_PORT hint was found in the lifecycle script, and APP_URL "
                    f"{application_url} {reachability_detail or 'did not respond'}."
                )
            return (
                "No APP_PORT or APP_URL hint was found in the lifecycle script, so "
                "OrchFlow cannot inspect a local process or reachability target for this "
                "project yet."
            )
        if status == "running":
            reason = f"Found {process_count} process(es) listening on APP_PORT {known_port}."
            if application_url is not None:
                reachability = (
                    reachability_detail
                    if reachability_detail
                    else ("reachable" if application_reachable else "not reachable")
                )
                return f"{reason} APP_URL {application_url} {reachability}."
            return reason
        if application_url is not None and application_reachable:
            return (
                f"No listening process was found for APP_PORT {known_port}, but APP_URL "
                f"{application_url} {reachability_detail or 'responded'}."
            )
        if application_url is not None:
            return (
                f"No listening process was found for APP_PORT {known_port}, and APP_URL "
                f"{application_url} {reachability_detail or 'did not respond'}."
            )
        return f"No listening process was found for APP_PORT {known_port}."

    def _load_process_snapshots(self, pids: list[int]) -> list[RuntimeProcessSnapshot]:
        if not pids:
            return []

        script = (
            "$ids = @(" + ",".join(str(pid) for pid in pids) + "); "
            "Get-Process -Id $ids -ErrorAction SilentlyContinue | "
            "Select-Object Id,ProcessName,CPU,WorkingSet64,StartTime | ConvertTo-Json"
        )
        completed = subprocess.run(
            [self.powershell_executable, "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            return []

        payload = json.loads(completed.stdout)
        items = payload if isinstance(payload, list) else [payload]
        snapshots: list[RuntimeProcessSnapshot] = []
        for item in items:
            started_at = self._parse_process_start_time(item.get("StartTime"))
            snapshots.append(
                RuntimeProcessSnapshot(
                    pid=int(item["Id"]),
                    name=str(item["ProcessName"]),
                    cpu_seconds=float(item["CPU"]) if item.get("CPU") is not None else None,
                    memory_bytes=(
                        int(item["WorkingSet64"])
                        if item.get("WorkingSet64") is not None
                        else None
                    ),
                    started_at=started_at,
                )
            )
        return snapshots

    @staticmethod
    def _parse_process_start_time(value: object) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None

        dotnet_match = DOTNET_JSON_DATE_PATTERN.match(value)
        if dotnet_match is not None:
            milliseconds = int(dotnet_match.group("milliseconds"))
            return datetime.fromtimestamp(milliseconds / 1000, tz=UTC)

        return datetime.fromisoformat(value).astimezone(UTC)
