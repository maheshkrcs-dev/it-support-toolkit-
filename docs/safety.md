# Safety, Privacy, and Limitations

## Scope

This project is for learning and authorized IT support. Run checks only on devices and networks you are permitted to troubleshoot.

## Read-only behavior

- The Python network utility performs DNS resolution and, unless `--dns-only` is selected, sends four ping requests.
- It passes arguments to `subprocess.run` as a list with `shell=False`, validates hostname/IP input, and enforces timeouts.
- The device information utility reads basic local OS, memory, and disk information. It does not read serial numbers, product keys, documents, passwords, or saved credentials.
- The PowerShell script queries basic Windows performance and operating-system information. It does not change services, registry values, firewall rules, updates, BitLocker, or other system settings.

## Interpret results carefully

- A failed ping can mean ICMP is blocked or filtered; it does not prove that a host or application is unavailable.
- DNS results depend on the current resolver, VPN, network, and local configuration.
- CPU load, memory, and disk values are point-in-time observations.
- Battery details may be unavailable on desktops or unsupported hardware.
- These scripts do not replace approved enterprise monitoring, security tools, or formal compliance checks.

## Data handling

Output is printed locally. Do not paste unredacted output into public issues or repositories. Review and sanitize hostnames, IP addresses, usernames, domain names, asset identifiers, and other organization-specific details before sharing.

## Corporate devices

Follow company policy and approved change-control procedures. Do not bypass execution policy, endpoint security, administrator controls, or network restrictions to run these tools.
