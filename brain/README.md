# brain — 树莓派大脑侧（Python）

EVA 的高层逻辑、视觉、语音与未来 AI 都在这里。

## 结构

| 路径 | 状态 | 说明 |
|------|------|------|
| `eva/protocol/` | **已实现** | EVA Module Protocol 帧编解码 + 能力描述符模型（传输无关） |
| `eva/transport/` | 抽象骨架 | `Transport` 接口；`SerialTransport` 见阶段1 |
| `eva/core/` | 抽象骨架 | `Module` 抽象 + `ModuleManager`（发现/注册/路由） |
| `eva/modules/` | 占位 | `CameraModule`/`MicModule`/`SpeakerModule` 见阶段1 |
| `eva/config/` | 占位 | 串口/引脚/地址配置 |

## 验证协议骨架

无需第三方依赖（仅标准库）：

```bash
cd brain
python -m eva.protocol   # encode→decode round-trip 自测 + CRC 校验
```

## 阶段1 依赖（届时在树莓派安装）

`pyserial`（串口）、`opencv-python`/`picamera2`（摄像头）、`sounddevice`/`numpy`（音频）。
见 `pyproject.toml` 的 `stage1` optional 分组。
