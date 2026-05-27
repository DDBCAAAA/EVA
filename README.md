# EVA — 模块化机器人

EVA 是一个可逐步扩展的模块化机器人项目。核心理念：**用统一的软硬件接口契约，让每个功能模块都能即插即用地接入系统**，从一个桌面机器人起步，逐步长成会移动、有手臂、能联网用 AI 的完整机器人。

## 架构总览

混合式计算架构：

- **大脑（brain）**：树莓派，跑 Linux + Python。负责高层逻辑、摄像头、语音（mic/speaker），以及未来的 AI。
- **协处理器（firmware）**：ESP32 / STM32，跑 C++ (PlatformIO)。负责实时性要求高的电机与传感器控制。
- **模块总线**：大脑与各协处理器之间用 **EVA Module Protocol** 通信。模块1用 USB/UART 直连，未来多模块可平滑迁移到 RS-485/CAN 多点总线。

新增一个硬件模块，只需满足三层契约：机械可对接、电气可接入总线、固件讲 EVA 协议并上报一份能力描述符。详见 [`docs/module-interface.md`](docs/module-interface.md)。

## 模块1：桌面机器人

第一个模块由 processor（树莓派）、摄像头、speaker、mic、一个电机组成。摄像头/mic/speaker 直接挂在树莓派上（本地模块），电机由 ESP32 底座控制器驱动（远程模块），从第一天就建立可复用的模块化范式。

## 仓库导航

| 目录 | 内容 |
|------|------|
| [`docs/`](docs/) | 架构、协议规范、模块接口契约、选型、路线图 |
| [`brain/`](brain/) | 树莓派侧 Python 代码（大脑） |
| [`firmware/`](firmware/) | 协处理器侧 C++/PlatformIO 固件 |
| [`hardware/`](hardware/) | 接线图、引脚分配、物料清单（BOM） |
| [`cad/`](cad/) | 3D 可打印模型与机械接口规范 |
| [`tools/`](tools/) | 烧录、串口监视等开发脚本 |

## 路线图（简）

- **阶段0**：仓库架构 + 设计文档 + 协议骨架 ← *当前*
- **阶段1**：模块1 跑通本地交互回路（离线）
- **阶段2**：WiFi 联网，重计算 offload 到 Mac mini，接入 AI
- **阶段3**：移动模块
- **阶段4**：手臂模块

完整路线见 [`docs/roadmap.md`](docs/roadmap.md)。

## 快速上手

当前阶段只有设计文档与协议骨架。可先验证协议编解码：

```bash
cd brain
python -m eva.protocol   # 运行内置 round-trip 自测
```
