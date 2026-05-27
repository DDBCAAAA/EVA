"""EVA Module Protocol —— 帧编解码与消息模型（传输无关）。

规范见 docs/module-protocol.md。固件侧常量镜像在 firmware/lib/eva_protocol/。
"""

from eva.protocol.messages import (
    PROTOCOL_VERSION,
    SOF,
    Address,
    MsgType,
    ErrorCode,
    Endpoint,
    CapabilityDescriptor,
    Frame,
)
from eva.protocol.codec import crc16_ccitt, encode, decode, FrameError

__all__ = [
    "PROTOCOL_VERSION",
    "SOF",
    "Address",
    "MsgType",
    "ErrorCode",
    "Endpoint",
    "CapabilityDescriptor",
    "Frame",
    "crc16_ccitt",
    "encode",
    "decode",
    "FrameError",
]
