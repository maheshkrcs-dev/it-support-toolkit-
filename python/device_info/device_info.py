#!/usr/bin/env python3
"""Display basic local device information without collecting serials or product keys."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import shutil
import subprocess
from typing import Any, List, Optional

BYTES_PER_GB = 1024 ** 3


def _memory_info() -> dict[str, Any]:
    """Return total/available RAM where supported, without third-party packages."""
    system = platform.system().lower()

    if system == "linux":
        values: dict[str, int] = {}
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as meminfo:
                for line in meminfo:
                    key, _, remainder = line.partition(":")
                    if key in {"MemTotal", "MemAvailable", "MemFree"}:
                        parts = remainder.split()
                        if parts:
                            values[key] = int(parts[0]) * 1024
            total = values.get("MemTotal")
            available = values.get("MemAvailable", values.get("MemFree"))
            if total is not None:
                result: dict[str, Any] = {"memory_total_gb": round(total / BYTES_PER_GB, 2)}
                if available is not None:
                    result["memory_available_gb"] = round(available / BYTES_PER_GB, 2)
                return result
        except (OSError, ValueError):
            pass
        return {"memory_information": "Unavailable"}

    if system == "windows":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        try:
            status = MEMORYSTATUSEX()
            status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return {"memory_information": "Unavailable"}
            return {
                "memory_total_gb": round(status.ullTotalPhys / BYTES_PER_GB, 2),
                "memory_available_gb": round(status.ullAvailPhys / BYTES_PER_GB, 2),
                "memory_used_percent": int(status.dwMemoryLoad),
            }
        except (AttributeError, OSError):
            return {"memory_information": "Unavailable"}

    if system == "darwin":
        # Use argv-based subprocess invocation; no shell and no user-controlled input.
        try:
            total_result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True,
                timeout=2.0, check=False, shell=False,
            )
            if total_result.returncode == 0:
                total = int(total_result.stdout.strip())
                return {"memory_total_gb": round(total / BYTES_PER_GB, 2),
                        "memory_available_information": "Not available via this basic check"}
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, OSError):
            pass
        return {"memory_information": "Unavailable"}

    return {"memory_information": "Unsupported operating system"}


def collect_info(include_hostname: bool = False) -> dict[str, Any]:
    """Collect a small, local-only inventory summary."""
    info: dict[str, Any] = {
        "operating_system": platform.system() or "Unknown",
        "os_release": platform.release() or "Unknown",
        "architecture": platform.machine() or "Unknown",
        "python_version": platform.python_version(),
        "logical_cpu_count": os.cpu_count(),
    }
    info.update(_memory_info())

    if include_hostname:
        info["hostname"] = platform.node()

    try:
        usage = shutil.disk_usage(os.path.abspath(os.sep))
        info["root_disk_total_gb"] = round(usage.total / BYTES_PER_GB, 2)
        info["root_disk_free_gb"] = round(usage.free / BYTES_PER_GB, 2)
        if usage.total > 0:
            info["root_disk_free_percent"] = round((usage.free / usage.total) * 100, 1)
    except OSError as exc:
        info["disk_information"] = f"Unavailable ({exc.__class__.__name__})"

    # Deliberately do not collect serial numbers, product keys, documents,
    # network credentials, user account names, or installed application lists.
    return info


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-hostname",
        action="store_true",
        help="Include the local hostname in output (omitted by default)",
    )
    args = parser.parse_args(argv)
    import json as _json
    print(_json.dumps(collect_info(args.include_hostname), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
