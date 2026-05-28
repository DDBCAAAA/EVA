"""无硬件端到端演示：大脑 ↔ 模拟底座模块（同进程，socketpair 链路）。

    cd brain && python -m eva.sim
"""

from __future__ import annotations

import time

from eva.core import ModuleManager
from eva.sim.base_module import BaseModuleSimulator
from eva.transport import SocketTransport


def run_demo() -> None:
    brain_link, module_link = SocketTransport.pair()

    simulator = BaseModuleSimulator(module_link, address=0x01)
    simulator.start()

    manager = ModuleManager(brain_link)

    print("→ 广播 DISCOVER，等待模块上报…")
    modules = manager.discover(timeout=0.5)
    for m in modules:
        print(f"← 发现模块 0x{m.address:02X}: {m.name} v{m.descriptor.fw_version}")
        for ep in m.descriptor.endpoints:
            print(f"    端点[{ep.id}] {ep.name} ({ep.type}) {ep.unit} 范围 {ep.range}")

    motor = modules[0]
    print("\n→ 下发命令 base_spin = 128")
    motor.command("base_spin", 128)

    deadline = time.monotonic() + 0.5
    while motor.latest("base_spin") != 128 and time.monotonic() < deadline:
        manager.poll(timeout=0.05)
    print(f"← 遥测回报 base_spin = {motor.latest('base_spin')}")

    simulator.stop()
    brain_link.close()
    module_link.close()
    print("\n演示结束：发现 / 命令 / 遥测 全链路跑通（无需任何硬件）。")


if __name__ == "__main__":
    run_demo()
