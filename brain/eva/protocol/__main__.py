"""`python -m eva.protocol` —— 运行协议编解码 round-trip 自测。"""

from eva.protocol.codec import _selftest

if __name__ == "__main__":
    _selftest()
