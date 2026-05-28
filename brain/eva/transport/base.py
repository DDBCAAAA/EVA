"""Transport 抽象：传输无关的帧收发接口。

ModuleManager 只依赖该接口，因此从 USB 点对点迁移到 RS-485/CAN 总线时，上层无需改动。
具体实现（SerialTransport 等）在阶段1落地。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque

from eva.protocol import Frame, FrameParser, encode


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


class StreamTransport(Transport):
    """面向字节流链路的 Transport 基类。

    把成帧/校验逻辑（FrameParser + encode）集中在这里，子类只需实现两个原语：
    向链路写字节、从链路读"当前可读的字节"。SerialTransport / SocketTransport 共享这套逻辑，
    因此从 USB 串口迁移到 socket（如未来 Mac mini over TCP）时上层与成帧代码都不变。
    """

    def __init__(self) -> None:
        self._parser = FrameParser()
        self._inbox: deque[Frame] = deque()

    def open(self) -> None:  # 子类按需覆盖
        pass

    def close(self) -> None:  # 子类按需覆盖
        pass

    def send(self, frame: Frame) -> None:
        self._write_all(encode(frame))

    def recv(self, timeout: float | None = None) -> Frame | None:
        """单次尝试：读一批字节并解析；有完整帧则返回其一，否则返回 None。

        调用方（ModuleManager / 模拟器）以截止时间循环调用本方法。
        """
        if self._inbox:
            return self._inbox.popleft()
        data = self._read_some(timeout)
        if data:
            self._inbox.extend(self._parser.feed(data))
        return self._inbox.popleft() if self._inbox else None

    @abstractmethod
    def _write_all(self, data: bytes) -> None:
        """把全部字节写入链路。"""

    @abstractmethod
    def _read_some(self, timeout: float | None) -> bytes:
        """读取当前可读的字节；在 timeout 内无数据则返回 b""。"""
