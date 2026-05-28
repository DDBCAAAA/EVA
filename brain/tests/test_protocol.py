"""协议层测试：帧编解码 round-trip、CRC、流式 FrameParser 的分片/粘连/错位恢复。"""

import unittest

from eva.protocol import (
    Address,
    CapabilityDescriptor,
    Endpoint,
    Frame,
    FrameError,
    FrameParser,
    MsgType,
    decode,
    encode,
    pack_endpoint_scalar,
    unpack_endpoint_scalar,
)


def _announce() -> Frame:
    desc = CapabilityDescriptor(
        module_type="module1_base",
        fw_version="0.1.0",
        address=0x01,
        endpoints=[Endpoint(0, "actuator", "motor.dc", "base_spin", "pwm", (-255, 255))],
    )
    return Frame(type=MsgType.ANNOUNCE, src=0x01, dst=Address.BRAIN, seq=1, payload=desc.to_json())


class TestCodec(unittest.TestCase):
    def test_round_trip_with_descriptor(self):
        frame = _announce()
        back = decode(encode(frame))
        self.assertEqual(back, frame)
        desc = CapabilityDescriptor.from_json(back.payload)
        self.assertEqual(desc.module_type, "module1_base")
        self.assertEqual(desc.endpoints[0].range, (-255, 255))

    def test_round_trip_empty_payload(self):
        frame = Frame(type=MsgType.DISCOVER, src=Address.BRAIN, dst=Address.BROADCAST, seq=7)
        self.assertEqual(decode(encode(frame)), frame)

    def test_scalar_payload_signed(self):
        for value in (-255, -1, 0, 1, 128, 255):
            endpoint_id, decoded = unpack_endpoint_scalar(pack_endpoint_scalar(3, value))
            self.assertEqual((endpoint_id, decoded), (3, value))

    def test_crc_corruption_rejected(self):
        raw = bytearray(encode(_announce()))
        raw[-1] ^= 0xFF
        with self.assertRaises(FrameError):
            decode(bytes(raw))


class TestFrameParser(unittest.TestCase):
    def test_two_concatenated_frames(self):
        a = encode(_announce())
        b = encode(Frame(type=MsgType.HEARTBEAT, src=0x01, dst=Address.BRAIN))
        frames = FrameParser().feed(a + b)
        self.assertEqual([f.type for f in frames], [MsgType.ANNOUNCE, MsgType.HEARTBEAT])

    def test_fragmented_byte_by_byte(self):
        raw = encode(_announce())
        parser = FrameParser()
        collected = []
        for i in range(len(raw)):
            collected += parser.feed(raw[i : i + 1])
        self.assertEqual(len(collected), 1)
        self.assertEqual(collected[0].type, MsgType.ANNOUNCE)

    def test_resync_after_garbage(self):
        raw = encode(_announce())
        frames = FrameParser().feed(b"\x00\xff\x7e garbage" + raw)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].type, MsgType.ANNOUNCE)

    def test_corrupt_frame_dropped_then_recover(self):
        good = encode(_announce())
        bad = bytearray(encode(_announce()))
        bad[-1] ^= 0xFF  # 坏 CRC
        frames = FrameParser().feed(bytes(bad) + good)
        # 坏帧被丢弃并重新对齐，后面那条好帧仍被解析出来
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].type, MsgType.ANNOUNCE)


if __name__ == "__main__":
    unittest.main()
