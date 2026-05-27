# 系统架构

## 设计目标

1. **模块化**：每个功能单元（底座、移动、手臂、联网……）都是可独立开发、可热插拔接入的模块。
2. **增量演进**：从模块1起步，新增模块不应迫使既有代码返工。
3. **职责分层**：高层智能与实时控制分离，各用最合适的平台与语言。

## 计算分层

```
        ┌─────────────────────────────────────────────┐
        │  大脑 Brain — 树莓派 (Linux + Python)         │
        │  高层编排 / 视觉 / 语音 / 未来 AI              │
        │                                               │
        │  本地模块（直挂 Pi）: 摄像头 · mic · speaker   │
        └───────────────┬─────────────────────────────┘
                        │  EVA Module Protocol
                        │  (USB/UART → 未来 RS-485/CAN)
        ┌───────────────┴─────────────────────────────┐
        │  协处理器 Co-processor — ESP32/STM32 (C++)    │
        │  实时电机 / 传感器控制                         │
        │                                               │
        │  远程模块: 底座电机 (模块1) · 未来移动/手臂     │
        └─────────────────────────────────────────────┘
```

- **为什么混合**：摄像头处理、语音、AI 需要 Linux 生态和算力 → 树莓派 + Python。电机 PWM、编码器读取、限位保护需要硬实时与确定性 → MCU + C++。两者各司其职，用协议解耦。
- **本地模块 vs 远程模块**：物理上挂在树莓派的外设（摄像头/mic/speaker）由大脑直接驱动，归类为"本地模块"；挂在某个 MCU 上的执行器/传感器（电机等）通过协议远程访问，归类为"远程模块"。两者在大脑侧共享统一的 `Module` 抽象（见 `brain/eva/core/module.py`）。

## 通信分层

EVA Module Protocol 是**传输无关**的帧协议：

- 模块1：树莓派 USB 直连一块 ESP32（点对点 UART）。
- 多模块：迁移到 RS-485 或 CAN 多点总线，靠帧里的 `SRC/DST` 地址寻址，协议本身不变。

协议完整规范见 [`module-protocol.md`](module-protocol.md)。

## 模块发现与即插即用

1. 模块上电 → 通过 `ANNOUNCE` 上报**能力描述符**（自己是什么类型、固件版本、有哪些 actuator/sensor 端点）。
2. 大脑的 `ModuleManager` 收到后，据描述符**动态构建模块代理**对象，无需为每种模块硬编码。
3. 之后大脑用 `COMMAND` 下发指令、模块用 `TELEMETRY` 上报状态，`HEARTBEAT` 维持在线判定。

这意味着：未来加一个手臂模块，大脑侧不必改核心代码——它会被自动发现并以其能力描述符暴露给上层逻辑。

## 软件结构（大脑侧）

```
brain/eva/
├── protocol/   帧编解码 + 消息定义 + 能力描述符模型（传输无关）
├── transport/  Transport 抽象（SerialTransport / 未来 BusTransport）
├── core/       Module 抽象 + ModuleManager（发现/注册/路由）
├── modules/    具体能力驱动（camera/mic/speaker 本地，motor 远程）
└── config/     模块与引脚配置
```

依赖方向：`modules` → `core` → `transport` / `protocol`。`protocol` 不依赖任何上层，便于在测试和工具中独立复用，也便于固件侧（`firmware/lib/eva_protocol`）保持镜像一致。

## 相关文档

- 协议帧与消息：[`module-protocol.md`](module-protocol.md)
- 新增模块的三层契约：[`module-interface.md`](module-interface.md)
- 硬件选型与 BOM：[`hardware-selection.md`](hardware-selection.md)
- 路线图：[`roadmap.md`](roadmap.md)
