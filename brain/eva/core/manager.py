"""ModuleManager：模块发现、注册与消息路由（骨架）。

职责（阶段1落地）：
1. 通过 Transport 广播 DISCOVER，收集各模块的 ANNOUNCE 能力描述符。
2. 据描述符为每个远程模块动态构建 RemoteModule 代理并注册。
3. 路由 COMMAND/TELEMETRY/ACK/ERROR，按 SEQ 匹配确认，按 HEARTBEAT 超时判离线。

本阶段仅定义接口与注册表骨架；收发循环留到阶段1。
"""

from __future__ import annotations

from eva.core.module import Module, RemoteModule
from eva.protocol import CapabilityDescriptor, Frame, MsgType
from eva.transport import Transport


class ModuleManager:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self._modules: dict[int, Module] = {}

    def register(self, address: int, module: Module) -> None:
        self._modules[address] = module

    def get(self, address: int) -> Module | None:
        return self._modules.get(address)

    def discover(self, timeout: float = 1.0) -> list[Module]:
        """广播 DISCOVER 并收集 ANNOUNCE，构建远程模块代理。"""
        # 阶段1实现：发 DISCOVER → 在 timeout 内收集 ANNOUNCE → _on_announce
        raise NotImplementedError

    def _on_announce(self, frame: Frame) -> RemoteModule:
        descriptor = CapabilityDescriptor.from_json(frame.payload)
        module = RemoteModule(address=frame.src, descriptor=descriptor)
        self.register(frame.src, module)
        return module

    def route(self, frame: Frame) -> None:
        """把收到的帧分发给对应处理逻辑（阶段1实现）。"""
        if frame.type is MsgType.ANNOUNCE:
            self._on_announce(frame)
            return
        raise NotImplementedError
