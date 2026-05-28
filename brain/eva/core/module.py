"""Module 抽象。

统一两类模块：
- LocalModule：物理上直挂树莓派的外设（摄像头/mic/speaker），由大脑直接驱动。
- RemoteModule：挂在某个协处理器(MCU)上的执行器/传感器，经 EVA 协议远程访问。

上层行为逻辑只面向 Module 接口，不关心模块在本地还是远程。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from eva.protocol import (
    CapabilityDescriptor,
    Endpoint,
    Frame,
    MsgType,
    pack_endpoint_scalar,
)

if TYPE_CHECKING:
    from eva.core.manager import ModuleManager


class Module(ABC):
    """一个功能模块的统一抽象。"""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...


class LocalModule(Module):
    """直挂树莓派的外设模块（摄像头/mic/speaker）。

    具体驱动在 eva.modules 实现（阶段1）。
    """


class RemoteModule(Module):
    """经 EVA 协议访问的远程模块（电机等，挂在 MCU 上）。

    由 ModuleManager 依据 ANNOUNCE 的能力描述符动态构建：每个 endpoint 暴露为
    可下发 COMMAND（actuator）或可读取最新 TELEMETRY（sensor）的访问代理。
    """

    def __init__(
        self,
        address: int,
        descriptor: CapabilityDescriptor,
        manager: "ModuleManager | None" = None,
    ) -> None:
        self.address = address
        self.descriptor = descriptor
        self._manager = manager
        self.telemetry: dict[int, int] = {}      # endpoint_id -> 最新值
        self.last_seen: float | None = None       # 心跳/任何收帧时间戳（单调时钟）
        self._by_name = {ep.name: ep for ep in descriptor.endpoints}
        self._by_id = {ep.id: ep for ep in descriptor.endpoints}

    @property
    def name(self) -> str:
        return self.descriptor.module_type

    def endpoint(self, key: int | str) -> Endpoint:
        return self._by_id[key] if isinstance(key, int) else self._by_name[key]

    def command(self, key: int | str, value: int) -> None:
        """向某个执行器端点下发标量命令（如电机 PWM）。"""
        ep = self.endpoint(key)
        lo, hi = ep.range
        if not (lo <= value <= hi):
            raise ValueError(f"{ep.name}={value} 超出范围 {ep.range}")
        payload = pack_endpoint_scalar(ep.id, value)
        self._manager.send_frame(
            Frame(type=MsgType.COMMAND, dst=self.address, payload=payload)
        )

    def latest(self, key: int | str) -> int | None:
        """读取某端点最近一次上报的遥测值；尚无则返回 None。"""
        return self.telemetry.get(self.endpoint(key).id)

    def start(self) -> None:  # 阶段1：可在此发起心跳监听/订阅
        pass

    def stop(self) -> None:
        pass
