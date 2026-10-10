# IT Support Toolkit

Practical, safety-first utilities for desktop support and IT infrastructure learning.

**Status:** Initial draft — scripts and tests should be reviewed and run in your own lab before use. This is not an enterprise management or remediation tool.

## Included tools

| Tool | Purpose | Platform |
|---|---|---|
| Network Diagnostics | Validates host input, resolves DNS in a bounded subprocess, and optionally runs a bounded ping test | Windows, Linux, macOS (ping flags differ by OS) |
| Device Information | Displays basic OS, CPU, memory, and root/system-drive disk information | Windows, Linux, macOS (memory fields vary by OS) |
| System Health Check | Reports CIM-reported CPU load, memory, system-drive space, uptime, and battery status when available | Windows PowerShell 5.1+ |

These tools are intended to be read-only. Network Diagnostics sends four ICMP echo requests only when you explicitly run the ping check. No third-party Python packages are required.

## Requirements

- Python 3.9 or newer for Python tools
- Windows PowerShell 5.1+ or PowerShell 7 on Windows for the system health check

## Run Network Diagnostics

```bash
python python/network_diagnostics/network_diagnostics.py example.com
```

DNS only (no ping requests):

```bash
python python/network_diagnostics/network_diagnostics.py example.com --dns-only
```

DNS resolution runs in a child process with a timeout. The ping test also has an overall timeout. A failed ping does not prove a service is down; ICMP may be blocked.

## Run Device Information

```bash
python python/device_info/device_info.py
```

By default, the hostname is omitted. Include it only when needed:

```bash
python python/device_info/device_info.py --include-hostname
```

Review output before sharing it publicly.

## Run Windows System Health Check

In PowerShell:

```powershell
.\powershell\system_health\Get-SystemHealth.ps1
```

Follow your organization's approved procedures if execution is restricted. Do not bypass company policy or lower security controls to run this script.

## Tests

Run from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover validation, mocked DNS/ping behavior, timeouts, and device-information privacy/error handling. They do not send network traffic.

## Safety and privacy

- Use only on devices and networks you are authorized to troubleshoot.
- Commands are run without a shell using untrusted host input.
- Reports print locally; tools do not automatically upload or save device data.
- Never commit credentials, tokens, product keys, internal hostnames, employee information, or real asset inventories.
- The PowerShell check is informational, not a security or compliance certification. Some values may be unavailable depending on hardware, OS, and permissions.

See [`docs/safety.md`](docs/safety.md) for details.

## Roadmap

- [ ] Test the scripts on Windows and Ubuntu
- [ ] Add verified, sanitized screenshots and real sample output
- [ ] Add new checks only after documenting limitations and testing them
- [ ] Choose a repository license before publishing one

## Maintainer

Mahesh Kumar · [GitHub](https://github.com/maheshkrcs-dev) · [Portfolio](https://maheshkrcs-dev.github.io/)
