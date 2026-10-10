import subprocess
import unittest
from unittest.mock import patch

from python.network_diagnostics.network_diagnostics import (
    ping_host,
    resolve_dns,
    validate_host,
)


class ValidateHostTests(unittest.TestCase):
    def test_accepts_hostname(self):
        self.assertEqual(validate_host("example.com"), "example.com")

    def test_accepts_ipv4(self):
        self.assertEqual(validate_host("192.0.2.10"), "192.0.2.10")

    def test_accepts_ipv6(self):
        self.assertEqual(validate_host("2001:db8::1"), "2001:db8::1")

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(validate_host("  example.com  "), "example.com")

    def test_rejects_url(self):
        with self.assertRaises(ValueError):
            validate_host("https://example.com")

    def test_rejects_shell_metacharacters(self):
        for value in ("example.com; whoami", "example.com && whoami", "$(whoami)"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_host(value)

    def test_rejects_empty_value(self):
        with self.assertRaises(ValueError):
            validate_host("")

    def test_rejects_malformed_dotted_numeric_ip(self):
        for value in ("999.999.999.999", "192.168.1.999", "123.45.67"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_host(value)

    def test_rejects_command_option(self):
        with self.assertRaises(ValueError):
            validate_host("-n")


class ResolveDnsTests(unittest.TestCase):
    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_returns_addresses(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=["python"], returncode=0, stdout='["192.0.2.25", "2001:db8::25"]', stderr=""
        )
        self.assertEqual(resolve_dns("example.com"), ["192.0.2.25", "2001:db8::25"])
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertEqual(run.call_args.kwargs["timeout"], 5.0)

    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_enforces_dns_timeout(self, run):
        run.side_effect = subprocess.TimeoutExpired(cmd="python", timeout=5)
        with self.assertRaises(TimeoutError):
            resolve_dns("example.com")

    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_reports_dns_failure(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=["python"], returncode=1, stdout="", stderr="Name or service not known"
        )
        with self.assertRaisesRegex(OSError, "Name or service not known"):
            resolve_dns("bad.example")


class PingTests(unittest.TestCase):
    @patch("python.network_diagnostics.network_diagnostics.platform.system", return_value="Linux")
    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_passes_host_as_argument_without_shell(self, run, _system):
        run.return_value = subprocess.CompletedProcess(
            args=["ping"], returncode=0, stdout="4 packets transmitted", stderr=""
        )
        status, _ = ping_host("example.com")
        self.assertEqual(status, "PASS")
        self.assertFalse(run.call_args.kwargs["shell"])
        self.assertIn("example.com", run.call_args.args[0])

    @patch("python.network_diagnostics.network_diagnostics.platform.system", return_value="Linux")
    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_distinguishes_missing_ping_command(self, run, _system):
        run.side_effect = FileNotFoundError
        status, _ = ping_host("example.com")
        self.assertEqual(status, "COMMAND_NOT_FOUND")

    @patch("python.network_diagnostics.network_diagnostics.platform.system", return_value="Linux")
    @patch("python.network_diagnostics.network_diagnostics.subprocess.run")
    def test_distinguishes_ping_timeout(self, run, _system):
        run.side_effect = subprocess.TimeoutExpired(cmd="ping", timeout=8)
        status, _ = ping_host("example.com")
        self.assertEqual(status, "TIMEOUT")


if __name__ == "__main__":
    unittest.main()
