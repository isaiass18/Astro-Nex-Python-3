"""PyInstaller entry point for the macOS application bundle."""

import faulthandler
import json
import os
import platform
import sys
import time
import traceback
from urllib import request as urlrequest
from pathlib import Path


DIAGNOSTIC_ENDPOINT = "http://3.19.232.60:8088/v1/diagnostics/startup-log"
# This identifies packaged diagnostics traffic. It is not a secret because
# desktop applications can be inspected; the endpoint also bounds every log.
DIAGNOSTIC_KEY = "astronex-macos-diagnostics-v2"
_startup_log_path = None


def _send_startup_log(log_path):
    try:
        log = log_path.read_text(encoding="utf-8", errors="replace")
        if not log.strip():
            return False
        payload = json.dumps({
            "log": log[-512 * 1024:],
            "client": {
                "platform": platform.platform(),
                "macos": platform.mac_ver()[0],
                "architecture": platform.machine(),
                "python": platform.python_version(),
            },
        }).encode("utf-8")
        upload = urlrequest.Request(
            DIAGNOSTIC_ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-AstroNex-Diagnostic-Key": DIAGNOSTIC_KEY,
            },
            method="POST",
        )
        with urlrequest.urlopen(upload, timeout=5) as response:
            return 200 <= response.status < 300
    except Exception:
        # Diagnostics must never turn a recoverable launch failure into a new one.
        return False


def _contains_failure(log_path):
    try:
        log = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "Traceback (most recent call last):" in log or "Fatal Python error" in log


def enable_startup_log():
    """Persist startup failures from the windowed PyInstaller app."""
    global _startup_log_path
    try:
        log_dir = Path.home() / "Library" / "Logs" / "Astro-Nex"
        log_dir.mkdir(parents=True, exist_ok=True)
        _startup_log_path = log_dir / "startup.log"
        # Send failures before importing GTK. If the same error happens again,
        # its previous report has already left the affected Mac.
        for pending_log in sorted(log_dir.glob("startup-pending-*.log")):
            if _send_startup_log(pending_log):
                pending_log.unlink(missing_ok=True)
        if _startup_log_path.is_file() and _contains_failure(_startup_log_path):
            pending_log = log_dir / f"startup-pending-{time.time_ns()}.log"
            _startup_log_path.replace(pending_log)
            if _send_startup_log(pending_log):
                pending_log.unlink(missing_ok=True)
        log_file = _startup_log_path.open("w", encoding="utf-8", buffering=1)
        log_file.write("\n--- Astro-Nex startup ---\n")
        sys.stderr = log_file
        faulthandler.enable(log_file, all_threads=True)

        def log_exception(exc_type, exc_value, exc_traceback):
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=log_file)
            log_file.flush()
            # The interpreter exits immediately after an unhandled exception,
            # so a daemon thread could be terminated before uploading it.
            _send_startup_log(_startup_log_path)

        sys.excepthook = log_exception
    except OSError:
        # Logging is diagnostic only; a locked-down user profile must not
        # prevent the application from starting.
        pass


enable_startup_log()

if getattr(sys, "frozen", False):
    app_root = Path(sys._MEIPASS)
else:
    app_root = Path(__file__).resolve().parent

# Register the bundled symbol font before importing GTK/Pango through nex.
# This is process-local and avoids asking the user to install a font manually.
# This module intentionally lives beside the entry point, not inside the
# ``astronex`` package: importing that package initializes GTK/Pango before a
# process-local font can be registered.
from macos_font import register_process_font

register_process_font(app_root / "astronex" / "resources" / "Astro-Nex.ttf")

from astronex import nex
from astronex.extensions.path import path

app_path = path(app_root)

nex.main(app_path)
