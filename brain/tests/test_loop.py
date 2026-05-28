"""端到端测试（无硬件）：大脑 ↔ 模拟底座模块，验证发现 / 命令 / 遥测全链路。

链路用 socket.socketpair 在同进程内构造，模拟器跑在后台线程。
"""

import time
import unittest

from eva.core import ModuleManager
from eva.core.module import RemoteModule
from eva.sim.base_module import BaseModuleSimulator
from eva.transport import SocketTransport


class TestBrainModuleLoop(unittest.TestCase):
    def setUp(self):
        self.brain_link, self.module_link = SocketTransport.pair()
        self.sim = BaseModuleSimulator(self.module_link, address=0x01, heartbeat_period=0.1)
        self.sim.start()
        self.manager = ModuleManager(self.brain_link)

    def tearDown(self):
        self.sim.stop()
        self.brain_link.close()
        self.module_link.close()

    def test_discover_finds_base_module(self):
        modules = self.manager.discover(timeout=0.5)
        self.assertEqual(len(modules), 1)
        module = modules[0]
        self.assertIsInstance(module, RemoteModule)
        self.assertEqual(module.name, "module1_base")
        self.assertEqual(module.address, 0x01)
        self.assertEqual(module.endpoint("base_spin").type, "motor.dc")

    def test_command_then_telemetry(self):
        [motor] = self.manager.discover(timeout=0.5)
        motor.command("base_spin", 128)

        deadline = time.monotonic() + 0.5
        while motor.latest("base_spin") != 128 and time.monotonic() < deadline:
            self.manager.poll(timeout=0.05)

        self.assertEqual(motor.latest("base_spin"), 128)
        self.assertEqual(self.manager.acks.get(0x01), self.manager._seq)

    def test_command_out_of_range_rejected(self):
        [motor] = self.manager.discover(timeout=0.5)
        with self.assertRaises(ValueError):
            motor.command("base_spin", 9999)


if __name__ == "__main__":
    unittest.main()
