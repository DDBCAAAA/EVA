"""EVA Module Protocol 的消息类型、地址、帧与能力描述符模型。

与 docs/module-protocol.md 保持一致。本模块不依赖任何上层，便于在测试与工具中独立复用。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import IntEnum

PROTOCOL_VERSION = 0x01
SOF = 0x7E  # 帧起始字节


class Address(IntEnum):
    """保留地址。1..0xFE 为模块地址。"""

    BRAIN = 0x00
    BROADCAST = 0xFF


class MsgType(IntEnum):
    ANNOUNCE = 0x01   # 模块→大脑：上报能力描述符
    DISCOVER = 0x02   # 大脑→广播：谁在线
    COMMAND = 0x03    # 大脑→模块：下发执行
    TELEMETRY = 0x04  # 模块→大脑：传感器/状态
    HEARTBEAT = 0x05  # 双向保活
    ACK = 0x06        # 双向确认
    ERROR = 0x07      # 双向错误


class ErrorCode(IntEnum):
    CRC_FAIL = 0x01
    UNKNOWN_TYPE = 0x02
    UNKNOWN_ENDPOINT = 0x03
    OUT_OF_RANGE = 0x04
    BUSY = 0x05


@dataclass
class Endpoint:
    """模块暴露的一个执行器或传感器端点。"""

    id: int
    kind: str   # "actuator" | "sensor"
    type: str   # 如 "motor.dc" / "motor.servo" / "sensor.encoder"
    name: str
    unit: str
    range: tuple[float, float]


@dataclass
class CapabilityDescriptor:
    """ANNOUNCE 负载：模块的自描述，大脑据此动态构建访问代理。"""

    module_type: str
    fw_version: str
    address: int
    endpoints: list[Endpoint] = field(default_factory=list)

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")

    @classmethod
    def from_json(cls, payload: bytes) -> "CapabilityDescriptor":
        obj = json.loads(payload.decode("utf-8"))
        endpoints = [Endpoint(**ep) if not isinstance(ep, Endpoint) else ep
                     for ep in obj.get("endpoints", [])]
        # json 把 tuple 还原成 list，统一转回 tuple
        for ep in endpoints:
            ep.range = tuple(ep.range)
        return cls(
            module_type=obj["module_type"],
            fw_version=obj["fw_version"],
            address=obj["address"],
            endpoints=endpoints,
        )


@dataclass
class Frame:
    """一条完整的协议帧。

    payload 的解释取决于 type（见 docs/module-protocol.md）。
    """

    type: MsgType
    src: int = Address.BRAIN
    dst: int = Address.BROADCAST
    seq: int = 0
    payload: bytes = b""
    ver: int = PROTOCOL_VERSION
