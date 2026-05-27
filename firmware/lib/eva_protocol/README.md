# eva_protocol（C++）

与 `brain/eva/protocol/` 镜像的协议实现：帧编解码、CRC-16/CCITT-FALSE、消息类型与地址常量。

**约定**：两侧的帧布局、CRC 算法、消息类型编号、能力描述符字段必须严格一致；
任何破坏性变更都要同步两侧并递增帧 `VER`（见 [`../../../docs/module-protocol.md`](../../../docs/module-protocol.md)）。

阶段1实现，建议含一个最小自测以与 Python 侧的 round-trip 结果对齐。
