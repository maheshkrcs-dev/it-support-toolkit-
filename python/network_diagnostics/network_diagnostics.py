#!/usr/bin/env python3
"""Read-only, bounded network checks for IT support practice."""

from __future__ import annotations

import argparse
import ipaddress
import json
import platform
import re
import subprocess
import sys
from typing import Optional

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\\."
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\\.?$"
)
DNS_TIMEOUT_SECONDS = 5.0
PING_TIMEOUT_SECONDS = 8.0


def validate_host(value: str) -> str:
    """Accept an IP address or DNS hostname; reject URLs and command syntax."""
    host = value.strip()
    if not host or any(ch.isspace() for ch in host):
        raise ValueError("Enter a hostname or IP address without spaces.")
    if "://" in host or "/" in host or "\\" in host or host.startswith("-"):
        raise ValueError("Enter a hostname or IP address, not a URL or command option.")

    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        # A dotted string containing only digits and dots is intended to be IPv4.
        # Do not accidentally accept malformed IPv4 as a DNS hostname.
        if re.fullmatch(r"[0-9.]+", host):
            raise ValueError("Invalid IP address.")
        if not HOSTNAME_RE.fullmatch(host):
            raise ValueError("Invalid hostname or IP address.")
        return host.rstrip(".")


def resolve_dns(host: str, timeout_seconds: float = DNS_TIMEOUT_SECONDS) -> list[str]:
    """Resolve a host in a child process so the lookup has an enforceable timeout."""
    resolver_code = (
        "import json,socket,sys; "
        "host=sys.argv[1]; "
        "results=socket.getaddrinfo(host,None,type=socket.SOCK_STREAM); "
        "print(json.dumps(sorted({item[4][0] for item in results})))"
    )
    try:
        result = subprocess.run(
            [sys.executable, "-c", resolver_code, host],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"DNS lookup exceeded {timeout_seconds:g} seconds.") from exc

    if result.returncode != 0:
        detail = (result.stderr or "DNS resolution failed.").strip()
        raise OSError(detail)
    try:
        addresses = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise OSError("DNS resolver returned an unreadable response.") from exc
    if not isinstance(addresses, list) or not all(isinstance(x, str) for x in addresses):
        raise OSError("DNS resolver returned an unexpected response.")
    if not addresses:
        raise OSError("DNS returned no addresses.")
    return addresses


def ping_host(host: str, timeout_seconds: float = PING_TIMEOUT_SECONDS) -> tuple[str, str]:
    """Run four ping attempts without a shell and enforce an overall timeout."""
    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", "4", "-w", "1000", host]
    elif system == "linux":
        command = ["ping", "-c", "4", "-W", "1", host]
    elif system == "darwin":
        command = ["ping", "-c", "4", host]
    else:
        return "UNSUPPORTED", f"Ping is not configured for operating system: {platform.system()}"

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        return "COMMAND_NOT_FOUND", "The ping command was not found on this system."
    except subprocess.TimeoutExpired:
        return "TIMEOUT", f"Ping exceeded the {timeout_seconds:g}-second time limit."

    output = (result.stdout or result.stderr).strip()
    if result.returncode == 0:
        return "PASS", output or "Ping completed successfully."
    return "NO_REPLY", output or f"Ping returned exit code {result.returncode}."


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Perform bounded DNS and ping checks for an authorized host."
    )
    parser.add_argument("host", help="Hostname or IP address (not a URL)")
    parser.add_argument(
        "--dns-only", action="store_true", help="Resolve DNS only; do not send ping requests"
    )
    args = parser.parse_args(argv)

    try:
        host = validate_host(args.host)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    print(f"Network diagnostics for: {host}")
    print("-" * 40)
    try:
        addresses = resolve_dns(host)
        print("DNS: PASS")
        for address in addresses:
            print(f"  Address: {address}")
    except TimeoutError as exc:
        print(f"DNS: TIMEOUT ({exc})")
        if not args.dns_only:
            print("Ping: SKIPPED because DNS did not complete.")
        return 1
    except OSError as exc:
        print(f"DNS: FAIL ({exc})")
        if not args.dns_only:
            print("Ping: SKIPPED because DNS resolution failed.")
        return 1

    if args.dns_only:
        return 0

    status, detail = ping_host(host)
    labels = {
        "PASS": "PASS",
        "NO_REPLY": "FAIL / NO REPLY",
        "TIMEOUT": "TIMEOUT",
        "COMMAND_NOT_FOUND": "UNAVAILABLE",
        "UNSUPPORTED": "UNSUPPORTED",
    }
    print(f"Ping: {labels.get(status, status)}")
    if detail:
        print(detail)
    if status != "PASS":
        print("Note: ICMP may be blocked; this alone does not prove a service is down.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
