"""传输层：把协议帧搬运到物理链路上。

- Transport：抽象接口。
- StreamTransport：面向字节流的基类（成帧/校验逻辑集中于此）。
- SocketTransport：socketpair/TCP，用于无硬件测试与未来 Mac mini 链路。
- SerialTransport：USB/UART，模块1（依赖 pyserial，延迟导入）。

未来 BusTransport（RS-485/CAN 多点）在阶段3加入。
"""

from eva.transport.base import Transport, StreamTransport
from eva.transport.net import SocketTransport
from eva.transport.serial import SerialTransport

__all__ = ["Transport", "StreamTransport", "SocketTransport", "SerialTransport"]
