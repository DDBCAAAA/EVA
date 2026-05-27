"""Transport 抽象：传输无关的帧收发接口。

ModuleManager 只依赖该接口，因此从 USB 点对点迁移到 RS-485/CAN 总线时，上层无需改动。
具体实现（SerialTransport 等）在阶段1落地。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from eva.protocol import Frame


class Transport(ABC):
    """收发 EVA 协议帧的物理链路抽象。"""

    @abstractmethod
    def open(self) -> None:
        """建立链路。"""

    @abstractmethod
    def close(self) -> None:
        """关闭链路。"""

    @abstractmethod
    def send(self, frame: Frame) -> None:
        """编码并发送一帧。"""

    @abstractmethod
    def recv(self, timeout: float | None = None) -> Frame | None:
        """接收一帧；超时返回 None。

        实现需负责从字节流中按 SOF 对齐、按 LEN 取整帧、校验 CRC（见 eva.protocol.codec）。
        """
