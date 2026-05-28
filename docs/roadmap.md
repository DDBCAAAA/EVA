# 路线图

模块化、增量演进。每个阶段产出可运行/可验证的成果，不为后续阶段欠下返工债。

## 阶段0 — 地基（当前）

- [x] 仓库目录结构
- [x] 核心设计文档（架构、协议、模块接口、选型、路线图）
- [x] EVA Module Protocol 帧编解码 + 能力描述符模型（Python 骨架，含 round-trip 自测）
- [x] 大脑侧抽象骨架：`Transport` / `Module` / `ModuleManager`

## 阶段1 — 模块1 桌面机器人（离线）

目标：Pi 大脑 + 底座（ESP32 + 1 电机） + 摄像头/mic/speaker，跑通本地交互回路，**无需联网**。

无硬件部分已先行落地（等板子期间用模拟器开发）：

- [x] `brain/eva/transport`：`StreamTransport` + `SocketTransport` + `SerialTransport`（pyserial 延迟导入）
- [x] `brain/eva/core/manager`：发现/注册/路由/遥测落地
- [x] `brain/eva/core/module`：`RemoteModule` 端点代理（按能力描述符动态构建）
- [x] `brain/eva/sim`：`BaseModuleSimulator` + 端到端演示（`python -m eva.sim`）
- [x] 测试：协议分片/粘连/错位恢复 + 大脑↔模块全链路（`python -m unittest`）

待硬件到货：

- [ ] `firmware/modules/module1_base`：ESP32 固件，驱动电机、实现 ANNOUNCE/COMMAND/TELEMETRY/HEARTBEAT（行为对齐模拟器）
- [ ] 把编排里的 `SocketTransport` 换成 `SerialTransport`，接真实底座
- [ ] `brain/eva/modules`：`CameraModule`/`MicModule`/`SpeakerModule`（本地）
- [ ] 一个最小行为回路（如：看到人脸 → 电机转向 → 说一句话）
- [ ] `cad/module1-base`：外壳与 EVA Mount 实体建模并打印

## 阶段2 — 联网 + AI（Mac mini）

目标：把视觉/LLM/语音等重计算 offload 到 Mac mini，接入 AI。

- [ ] Pi ↔ Mac mini 网络通道（WiFi）
- [ ] Mac mini 侧推理服务（视觉/语音/LLM）
- [ ] 大脑侧 AI 客户端与本地行为编排融合
- [ ] 离线兜底策略（断网时退回阶段1的本地行为）

## 阶段3 — 移动模块

- [ ] 移动底盘固件（新 ESP32 节点接入总线）
- [ ] 多模块总线迁移（USB 点对点 → RS-485/CAN），验证 SRC/DST 寻址
- [ ] 大脑侧运动控制
- [ ] 底盘机械件

## 阶段4 — 手臂模块

- [ ] 多关节固件 + 能力描述符
- [ ] 大脑侧逆运动学/抓取行为
- [ ] 手臂机械件

## 跨阶段约束

- 任何破坏协议兼容的改动都要递增帧 `VER` 并更新 [`module-protocol.md`](module-protocol.md)。
- 新增模块遵循 [`module-interface.md`](module-interface.md) 的三层契约与 checklist。
