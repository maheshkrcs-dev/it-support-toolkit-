# IT Support Toolkit

[![Python Tests](https://github.com/maheshkrcs-dev/it-support-toolkit-/actions/workflows/python-tests.yml/badge.svg)](https://github.com/maheshkrcs-dev/it-support-toolkit-/actions/workflows/python-tests.yml)

Practical, safety-first utilities for desktop support and IT infrastructure learning.

**Project status:** Early-stage portfolio project. The Python test workflow has passed on Ubuntu, Windows, and macOS with Python 3.11 and 3.12. The Windows PowerShell health-check script still needs hands-on validation on a Windows device.

## What it demonstrates

- **Troubleshooting:** validate a hostname/IP, check DNS resolution, and optionally test ICMP reachability.
- **Endpoint information:** collect a small local summary of OS, architecture, CPU count, memory, and system-drive storage.
- **Windows health checks:** query basic CPU, memory, uptime, system-drive, and battery information with PowerShell.
- **Safe scripting habits:** bounded timeouts, argument-list subprocess calls, no shell execution for user-supplied hosts, privacy-conscious output, and unit tests.

## Tools

| Tool | Purpose | Platform |
|---|---|---|
| Network Diagnostics | DNS lookup and optional four-packet ping test | Windows, Linux, macOS (ping flags vary) |
| Device Information | Basic OS, CPU, memory, and root/system-drive disk summary | Windows, Linux, macOS (memory fields vary) |
| System Health Check | CIM-based CPU load, memory, system-drive space, uptime, and battery status when available | Windows PowerShell 5.1+ |

No third-party Python packages are required for the Python tools.

## Quick start

Clone the repository and open its directory:

```bash
git clone https://github.com/maheshkrcs-dev/it-support-toolkit-.git
cd it-support-toolkit-
python --version
```

Use Python 3.9 or newer.

### 1. Check DNS only

This mode resolves a hostname without sending ping requests:

```bash
python python/network_diagnostics/network_diagnostics.py example.com --dns-only
```

### 2. Check DNS and ping

This sends four ICMP echo requests after DNS succeeds:

```bash
python python/network_diagnostics/network_diagnostics.py example.com
```

A failed ping does not prove a website or service is down; ICMP can be filtered. See the [network troubleshooting demo](docs/network-troubleshooting-demo.md) for a step-by-step workflow.

### 3. Collect basic device information

```bash
python python/device_info/device_info.py
```

The hostname is omitted by default. Include it only when needed:

```bash
python python/device_info/device_info.py --include-hostname
```

Review output before sharing it publicly.

### 4. Run the Windows health check

From PowerShell on Windows:

```powershell
.\powershell\system_health\Get-SystemHealth.ps1
```

The script is informational and read-only. It has not yet been validated on a physical Windows endpoint. Follow company-approved procedures if script execution is restricted; do not bypass endpoint controls.

## Automated tests

Run the suite from the repository root:

```bash
python -m unittest discover -s tests -v
python -m compileall -q python tests
```

**Verified CI evidence:** [GitHub Actions run — 6 of 6 jobs passed](https://github.com/maheshkrcs-dev/it-support-toolkit-/actions/runs/38056634555) on October 10, 2026. The matrix covers Python 3.11 and 3.12 on Ubuntu, Windows, and macOS. Tests mock DNS/ping subprocess behavior, so the test suite itself does not send network traffic. This result validates the Python tests and compilation on those runners; it does not validate the PowerShell script or every real-world network environment.

## Safety and privacy

- Run checks only on devices and networks you are authorized to troubleshoot.
- DNS and ping checks contact the target you specify; use `--dns-only` when you want to avoid ping requests.
- Commands are run without a shell using untrusted host input.
- Output is printed locally; the tools do not automatically upload or save device data.
- The device-information utility does not collect serial numbers, product keys, documents, passwords, saved credentials, or installed-app inventories.
- Never commit credentials, tokens, product keys, internal hostnames, employee information, or real asset inventories.
- These utilities are not enterprise monitoring, remediation, or compliance tools.

Read [Safety, Privacy, and Limitations](docs/safety.md) before use.

## Roadmap

- [x] Add cross-platform Python unit-test workflow
- [x] Document a repeatable network troubleshooting walkthrough
- [ ] Capture genuine, sanitized terminal screenshots from a local test run
- [ ] Validate the PowerShell health check on a Windows test device
- [ ] Choose a repository license before publishing one

## Maintainer

Mahesh Kumar · [GitHub](https://github.com/maheshkrcs-dev) · [Portfolio](https://maheshkrcs-dev.github.io/)
