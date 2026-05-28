"""模块1底座的无硬件模拟器。

行为对齐 firmware/modules/module1_base 的目标固件：
- 收到 DISCOVER → 回 ANNOUNCE（携带能力描述符）。
- 收到 COMMAND → 记录端点状态，回 ACK，并回一条反映新状态的 TELEMETRY。
- 周期性发 HEARTBEAT 保活。

把这块逻辑做成可注入任意 Transport 的对象：测试用 SocketTransport，
将来在真实/虚拟串口上跑就换 SerialTransport，行为不变。
"""

from __future__ import annotations

import threading
import time

from eva.protocol import (
    Address,
    CapabilityDescriptor,
    Endpoint,
    Frame,
    MsgType,
    pack_endpoint_scalar,
    unpack_endpoint_scalar,
)
from eva.transport import Transport


def default_base_descriptor(address: int = 0x01) -> CapabilityDescriptor:
    """模块1底座的默认能力描述符：一个直流电机端点。"""
    return CapabilityDescriptor(
        module_type="module1_base",
        fw_version="0.1.0",
        address=address,
        endpoints=[
            Endpoint(
                id=0,
                kind="actuator",
                type="motor.dc",
                name="base_spin",
                unit="pwm",
                range=(-255, 255),
            )
        ],
    )


class BaseModuleSimulator:
    def __init__(
        self,
        transport: Transport,
        descriptor: CapabilityDescriptor | None = None,
        address: int = 0x01,
        heartbeat_period: float = 1.0,
    ) -> None:
        self._t = transport
        self._addr = address
        self._descriptor = descriptor or default_base_descriptor(address)
        self._state: dict[int, int] = {ep.id: 0 for ep in self._descriptor.endpoints}
        self._heartbeat_period = heartbeat_period
        self._seq = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    # --- 生命周期 ---

    def start(self) -> threading.Thread:
        self._thread = threading.Thread(target=self.run, name="base-module-sim", daemon=True)
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

    def run(self) -> None:
        self._t.open()
        last_hb = 0.0
        try:
            while not self._stop.is_set():
                frame = self._t.recv(timeout=0.05)
                if frame is not None:
                    self._handle(frame)
                now = time.monotonic()
                if now - last_hb >= self._heartbeat_period:
                    self._send(Frame(type=MsgType.HEARTBEAT, dst=Address.BRAIN))
                    last_hb = now
        except (ConnectionError, OSError):
            pass  # 链路关闭，正常退出

    # --- 协议处理 ---

    def _handle(self, frame: Frame) -> None:
        if frame.type is MsgType.DISCOVER:
            self._send(Frame(type=MsgType.ANNOUNCE, dst=Address.BRAIN,
                             payload=self._descriptor.to_json()))
        elif frame.type is MsgType.COMMAND:
            endpoint_id, value = unpack_endpoint_scalar(frame.payload)
            self._state[endpoint_id] = value
            self._send(Frame(type=MsgType.ACK, dst=Address.BRAIN, payload=bytes([frame.seq])))
            self._send(Frame(type=MsgType.TELEMETRY, dst=Address.BRAIN,
                             payload=pack_endpoint_scalar(endpoint_id, value)))

    def _send(self, frame: Frame) -> None:
        frame.src = self._addr
        frame.seq = self._seq
        self._seq = (self._seq + 1) & 0xFF
        self._t.send(frame)
