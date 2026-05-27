"""Module 抽象。

统一两类模块：
- LocalModule：物理上直挂树莓派的外设（摄像头/mic/speaker），由大脑直接驱动。
- RemoteModule：挂在某个协处理器(MCU)上的执行器/传感器，经 EVA 协议远程访问。

上层行为逻辑只面向 Module 接口，不关心模块在本地还是远程。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from eva.protocol import CapabilityDescriptor


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
    可下发 COMMAND（actuator）或可订阅 TELEMETRY（sensor）的访问代理。
    """

    def __init__(self, address: int, descriptor: CapabilityDescriptor) -> None:
        self.address = address
        self.descriptor = descriptor

    @property
    def name(self) -> str:
        return self.descriptor.module_type

    def start(self) -> None:  # 阶段1：建立心跳/订阅
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
