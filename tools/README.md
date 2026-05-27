# tools — 开发脚本

辅助开发的脚本（阶段1按需添加）。规划：

- **串口监视/嗅探**：解码 EVA 协议帧，便于调试大脑↔模块通信。
- **固件烧录**：包装 `pio run -t upload`。
- **协议一致性检查**：用 `brain/eva/protocol` 生成测试帧，校验固件侧 `eva_protocol` 解析一致。

本阶段为占位。协议自测当前可直接运行：

```bash
cd brain && python -m eva.protocol
```
