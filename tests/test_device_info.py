import unittest
from unittest.mock import patch

from python.device_info.device_info import collect_info


class DeviceInfoTests(unittest.TestCase):
    @patch("python.device_info.device_info.shutil.disk_usage")
    @patch("python.device_info.device_info._memory_info", return_value={"memory_total_gb": 16.0})
    @patch("python.device_info.device_info.platform.node", return_value="PRIVATE-HOST")
    def test_hostname_is_omitted_by_default(self, _node, _memory, disk_usage):
        disk_usage.return_value = type("Usage", (), {"total": 100, "free": 25})()
        info = collect_info()
        self.assertNotIn("hostname", info)
        self.assertEqual(info["memory_total_gb"], 16.0)
        self.assertEqual(info["root_disk_free_percent"], 25.0)

    @patch("python.device_info.device_info.shutil.disk_usage")
    @patch("python.device_info.device_info._memory_info", return_value={"memory_information": "Unavailable"})
    @patch("python.device_info.device_info.platform.node", return_value="TEST-HOST")
    def test_hostname_only_when_explicitly_requested(self, _node, _memory, disk_usage):
        disk_usage.return_value = type("Usage", (), {"total": 100, "free": 25})()
        info = collect_info(include_hostname=True)
        self.assertEqual(info["hostname"], "TEST-HOST")

    @patch("python.device_info.device_info.shutil.disk_usage", side_effect=OSError("denied"))
    @patch("python.device_info.device_info._memory_info", return_value={"memory_information": "Unavailable"})
    def test_disk_failure_is_reported_without_crashing(self, _memory, _disk):
        info = collect_info()
        self.assertIn("disk_information", info)
        self.assertIn("Unavailable", info["disk_information"])

    @patch("python.device_info.device_info.platform.system", return_value="Linux")
    @patch("builtins.open", side_effect=OSError("not available"))
    def test_linux_memory_failure_is_graceful(self, _open, _system):
        from python.device_info.device_info import _memory_info
        self.assertEqual(_memory_info(), {"memory_information": "Unavailable"})


if __name__ == "__main__":
    unittest.main()
