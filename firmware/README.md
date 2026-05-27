# firmware — 协处理器侧（C++ / PlatformIO）

各硬件模块上 MCU（ESP32/STM32）的固件。负责实时电机与传感器控制，对大脑讲 EVA Module Protocol。

## 结构

| 路径 | 状态 | 说明 |
|------|------|------|
| `platformio.ini` | 骨架 | PlatformIO 环境（默认 ESP32-S3） |
| `lib/eva_protocol/` | 占位 | 与 `brain/eva/protocol/` 镜像的协议常量与帧编解码（C++），阶段1实现 |
| `modules/module1_base/` | 占位 | 模块1底座固件（驱动电机 + 协议收发），阶段1实现 |

## 固件职责（每个模块都需满足）

1. 上电后能响应 `DISCOVER`，以 `ANNOUNCE` 上报能力描述符。
2. 解析发给本地址的 `COMMAND`，按 `endpoint_id` 执行。
3. 按需 `TELEMETRY` 上报，周期 `HEARTBEAT` 保活。
4. 复用 `lib/eva_protocol`，与大脑侧协议版本一致。

详见 [`../docs/module-protocol.md`](../docs/module-protocol.md) 与 [`../docs/module-interface.md`](../docs/module-interface.md)。

## 构建（阶段1）

```bash
cd firmware
pio run -e module1_base            # 编译
pio run -e module1_base -t upload  # 烧录
```
