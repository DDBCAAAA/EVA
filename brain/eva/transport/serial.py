"""SerialTransport：基于 USB/UART 的 StreamTransport（模块1）。

依赖 pyserial，但**延迟到 open() 才导入**，因此在没装 pyserial 的开发机上也能 import 本模块、
跑其余测试。成帧/校验逻辑全部继承自 StreamTransport，与 SocketTransport 完全一致——
也就是说无硬件测试覆盖到的那套逻辑，正是真实串口要走的逻辑。

无硬件想试真实串口路径时，可用 socat 造一对虚拟串口::

    socat -d -d pty,raw,echo=0 pty,raw,echo=0
    # 把两端 /dev/pts/N 分别给大脑和模拟器
"""

from __future__ import annotations

from eva.transport.base import StreamTransport


class SerialTransport(StreamTransport):
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        super().__init__()
        self._port = port
        self._baudrate = baudrate
        self._ser = None

    def open(self) -> None:
        import serial  # 延迟导入

        self._ser = serial.Serial(self._port, self._baudrate, timeout=0)

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def _write_all(self, data: bytes) -> None:
        self._ser.write(data)

    def _read_some(self, timeout: float | None) -> bytes:
        self._ser.timeout = timeout
        n = self._ser.in_waiting or 1
        return self._ser.read(n)
