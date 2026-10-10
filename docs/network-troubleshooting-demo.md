# Network Troubleshooting Demo

This walkthrough shows how to use the toolkit as one part of a structured first-line investigation. Run it only from a device and network you are authorized to troubleshoot.

## Scenario

A user says, “A website is not opening.” Do not assume the cause is the website, DNS, or the user's laptop before collecting evidence.

## Step 1 — Check name resolution first

Run DNS-only mode:

```bash
python python/network_diagnostics/network_diagnostics.py example.com --dns-only
```

**What this checks:** whether the current system resolver can return addresses for the supplied hostname. DNS-only mode does not run ping.

**If DNS fails or times out:**

1. Confirm the hostname is spelled correctly.
2. Check whether other known hostnames resolve on the same device.
3. Compare with an approved second device or network, if permitted.
4. Review the configured DNS servers, VPN state, and relevant corporate guidance.
5. Record the exact error and escalate with sanitized evidence if needed.

Do not change DNS settings on a managed endpoint without authorization.

## Step 2 — Check ICMP reachability (optional)

If DNS succeeds and policy permits, run:

```bash
python python/network_diagnostics/network_diagnostics.py example.com
```

This repeats the DNS check and then sends four ping requests.

- **Ping passes:** the host responded to ICMP from this device at that moment. This does not prove that the website's HTTPS service is healthy.
- **No reply or timeout:** ICMP may be filtered, the host may be unreachable, or the network path may have a problem. Do not conclude the website is down from ping alone.
- **Ping command unavailable:** the operating system may not have the ping utility installed or available on PATH.

## Step 3 — Continue with the appropriate checks

If the issue persists, use your organization's approved tools and procedures to check:

- Whether the problem affects one user, one device, a subnet, or many users.
- Wi-Fi/Ethernet connection and IP configuration.
- Default gateway reachability and VPN status.
- Proxy settings and whether the destination's required port/service is reachable.
- Whether the issue reproduces in another approved browser or application.

Do not run additional scans or contact internal hosts unless you are authorized to do so.

## Step 4 — Write a useful ticket update

Record the time, affected user/device using approved internal fields, exact destination, test mode, DNS result, ping result if run, and the next action. Sanitize all output before putting it in a public issue or portfolio.

Example wording (replace placeholders with your actual findings):

> Investigated reported website access issue at [time]. DNS-only check for [hostname] returned [result]. ICMP check was [run/not run] and returned [result]. Ping results alone do not confirm application availability. Next step: [approved check or escalation].

## Evidence and reproducibility

The repository's [automated CI run](https://github.com/maheshkrcs-dev/it-support-toolkit-/actions/runs/38056634555) passed all six Python/OS matrix jobs. The tests mock network subprocesses; they validate handling and timeouts rather than measuring the live network.

The file [sample-network-output.txt](../examples/sample-network-output.txt) is explicitly illustrative, not a captured real run. For a portfolio screenshot, run the command in your own terminal, remove internal hostnames/IPs and personal information, and capture the actual result. Never present sample output as live test evidence.
