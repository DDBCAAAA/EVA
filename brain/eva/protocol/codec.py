"""EVA Module Protocol 帧编解码 + CRC-16/CCITT-FALSE。

帧布局（见 docs/module-protocol.md）::

    SOF(0x7E) | VER | SRC | DST | TYPE | SEQ | LEN | PAYLOAD[LEN] | CRC16(LE)

CRC 覆盖 VER..PAYLOAD（不含 SOF），CRC-16/CCITT-FALSE，小端存储。

运行内置 round-trip 自测::

    python -m eva.protocol
"""

from __future__ import annotations

from eva.protocol.messages import SOF, Frame, MsgType

# 不含 SOF 的固定头部长度：VER SRC DST TYPE SEQ LEN
_HEADER_LEN = 6
_CRC_LEN = 2
MAX_PAYLOAD = 255


class FrameError(ValueError):
    """帧格式或校验错误。"""


def crc16_ccitt(data: bytes) -> int:
    """CRC-16/CCITT-FALSE：poly=0x1021, init=0xFFFF, 无反射, xorout=0x0000。"""
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def encode(frame: Frame) -> bytes:
    """把 Frame 序列化成线缆字节。"""
    if len(frame.payload) > MAX_PAYLOAD:
        raise FrameError(f"payload too long: {len(frame.payload)} > {MAX_PAYLOAD}")
    body = bytes(
        [
            frame.ver & 0xFF,
            frame.src & 0xFF,
            frame.dst & 0xFF,
            int(frame.type) & 0xFF,
            frame.seq & 0xFF,
            len(frame.payload),
        ]
    ) + frame.payload
    crc = crc16_ccitt(body)
    return bytes([SOF]) + body + crc.to_bytes(2, "little")


def decode(data: bytes) -> Frame:
    """把一条完整帧的字节解析成 Frame，校验 SOF、长度与 CRC。"""
    if len(data) < 1 + _HEADER_LEN + _CRC_LEN:
        raise FrameError("frame too short")
    if data[0] != SOF:
        raise FrameError(f"bad SOF: {data[0]:#04x}")

    ver, src, dst, type_, seq, length = data[1:1 + _HEADER_LEN]
    expected_len = 1 + _HEADER_LEN + length + _CRC_LEN
    if len(data) != expected_len:
        raise FrameError(f"length mismatch: got {len(data)}, expected {expected_len}")

    body = data[1:1 + _HEADER_LEN + length]
    payload = data[1 + _HEADER_LEN:1 + _HEADER_LEN + length]
    crc_recv = int.from_bytes(data[-_CRC_LEN:], "little")
    crc_calc = crc16_ccitt(body)
    if crc_recv != crc_calc:
        raise FrameError(f"CRC mismatch: recv {crc_recv:#06x}, calc {crc_calc:#06x}")

    return Frame(
        type=MsgType(type_),
        src=src,
        dst=dst,
        seq=seq,
        payload=payload,
        ver=ver,
    )


def _selftest() -> None:
    """构造各类帧做 encode→decode round-trip，验证还原一致与 CRC。"""
    from eva.protocol.messages import (
        Address,
        CapabilityDescriptor,
        Endpoint,
    )

    # 1) 一个 ANNOUNCE 帧，携带模块1底座的能力描述符
    desc = CapabilityDescriptor(
        module_type="module1_base",
        fw_version="0.1.0",
        address=0x01,
        endpoints=[
            Endpoint(
                id=0,
                kind="actuator",
                type="motor.dc",
                name="base_spin",
                unit="pwm",
                range=(-255, 255),
            )
        ],
    )
    announce = Frame(
        type=MsgType.ANNOUNCE,
        src=0x01,
        dst=Address.BRAIN,
        seq=1,
        payload=desc.to_json(),
    )
    raw = encode(announce)
    back = decode(raw)
    assert back.type is MsgType.ANNOUNCE, back.type
    assert back.src == 0x01 and back.dst == Address.BRAIN
    assert back.seq == 1
    desc_back = CapabilityDescriptor.from_json(back.payload)
    assert desc_back == desc, (desc_back, desc)

    # 2) 空负载帧（DISCOVER 广播）
    discover = Frame(type=MsgType.DISCOVER, src=Address.BRAIN, dst=Address.BROADCAST, seq=2)
    assert decode(encode(discover)) == discover

    # 3) CRC 损坏应被拒绝
    corrupt = bytearray(raw)
    corrupt[-1] ^= 0xFF
    try:
        decode(bytes(corrupt))
    except FrameError:
        pass
    else:
        raise AssertionError("corrupt frame should have raised FrameError")

    print("protocol codec self-test OK:")
    print(f"  ANNOUNCE frame = {len(raw)} bytes, payload = {len(announce.payload)} bytes")
    print(f"  round-trip descriptor matches: {desc_back.module_type} v{desc_back.fw_version}")


if __name__ == "__main__":
    _selftest()
