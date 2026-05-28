"""SocketTransport：基于已连接 socket 的 StreamTransport。

用途：
- 无硬件测试/演示：用 socket.socketpair() 在同一进程里造一条双向链路，
  让大脑与"模拟底座模块"对接（见 eva.sim）。
- 未来阶段2：Pi ↔ Mac mini 走 TCP 时可直接复用本传输。
"""

from __future__ import annotations

import socket

from eva.transport.base import StreamTransport


class SocketTransport(StreamTransport):
    def __init__(self, sock: socket.socket) -> None:
        super().__init__()
        self._sock = sock

    @classmethod
    def pair(cls) -> tuple["SocketTransport", "SocketTransport"]:
        """返回一对互联的传输（基于 socket.socketpair），用于测试/演示。"""
        a, b = socket.socketpair()
        return cls(a), cls(b)

    def close(self) -> None:
        self._sock.close()

    def _write_all(self, data: bytes) -> None:
        self._sock.sendall(data)

    def _read_some(self, timeout: float | None) -> bytes:
        self._sock.settimeout(timeout)
        try:
            data = self._sock.recv(4096)
        except (socket.timeout, TimeoutError):
            return b""
        if data == b"":
            raise ConnectionError("socket closed by peer")
        return data
