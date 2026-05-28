"""ModuleManager：模块发现、注册与消息路由。

职责：
1. 通过 Transport 广播 DISCOVER，收集各模块的 ANNOUNCE 能力描述符。
2. 据描述符为每个远程模块动态构建 RemoteModule 代理并注册（即插即用）。
3. 路由 TELEMETRY/ACK/ERROR/HEARTBEAT：更新遥测、记录确认、刷新在线时间。

收发以"单次 recv + 路由"为原语（poll），调用方按截止时间循环。
"""

from __future__ import annotations

import time

from eva.core.module import Module, RemoteModule
from eva.protocol import Address, CapabilityDescriptor, Frame, MsgType, unpack_endpoint_scalar
from eva.transport import Transport


class ModuleManager:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self._modules: dict[int, Module] = {}
        self._seq = 0
        self.acks: dict[int, int] = {}  # src -> 最近被确认的 seq

    # --- 注册表 ---

    def register(self, address: int, module: Module) -> None:
        self._modules[address] = module

    def get(self, address: int) -> Module | None:
        return self._modules.get(address)

    @property
    def modules(self) -> list[Module]:
        return list(self._modules.values())

    # --- 发送 ---

    def _next_seq(self) -> int:
        self._seq = (self._seq + 1) & 0xFF
        return self._seq

    def send_frame(self, frame: Frame) -> None:
        """补全 src=BRAIN 与递增 seq 后发送。"""
        frame.src = Address.BRAIN
        frame.seq = self._next_seq()
        self._transport.send(frame)

    # --- 接收/路由 ---

    def poll(self, timeout: float = 0.1) -> Frame | None:
        """收一帧并路由；无帧返回 None。"""
        frame = self._transport.recv(timeout=timeout)
        if frame is not None:
            self.route(frame)
        return frame

    def discover(self, timeout: float = 1.0) -> list[RemoteModule]:
        """广播 DISCOVER，在 timeout 内收集 ANNOUNCE 并构建远程模块代理。"""
        self.send_frame(Frame(type=MsgType.DISCOVER, dst=Address.BROADCAST))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.poll(timeout=min(0.05, max(0.0, deadline - time.monotonic())))
        return [m for m in self._modules.values() if isinstance(m, RemoteModule)]

    def route(self, frame: Frame) -> None:
        module = self._modules.get(frame.src)
        if isinstance(module, RemoteModule):
            module.last_seen = time.monotonic()

        if frame.type is MsgType.ANNOUNCE:
            self._on_announce(frame)
        elif frame.type is MsgType.TELEMETRY:
            if isinstance(module, RemoteModule):
                endpoint_id, value = unpack_endpoint_scalar(frame.payload)
                module.telemetry[endpoint_id] = value
        elif frame.type is MsgType.ACK:
            if frame.payload:
                self.acks[frame.src] = frame.payload[0]
        elif frame.type in (MsgType.HEARTBEAT, MsgType.ERROR):
            pass  # 心跳已刷新 last_seen；ERROR 暂仅忽略（阶段1可加日志/重发）

    def _on_announce(self, frame: Frame) -> RemoteModule:
        descriptor = CapabilityDescriptor.from_json(frame.payload)
        module = RemoteModule(address=frame.src, descriptor=descriptor, manager=self)
        module.last_seen = time.monotonic()
        self.register(frame.src, module)
        return module
