"""传输层：把协议帧搬运到物理链路上。

本阶段只定义抽象 Transport（见 base.py）。具体实现：
- SerialTransport（USB/UART，模块1）—— 阶段1。
- BusTransport（RS-485/CAN 多点）—— 阶段3。
"""

from eva.transport.base import Transport

__all__ = ["Transport"]
