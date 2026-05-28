# brain — 树莓派大脑侧（Python）

EVA 的高层逻辑、视觉、语音与未来 AI 都在这里。

## 结构

| 路径 | 状态 | 说明 |
|------|------|------|
| `eva/protocol/` | **已实现** | 帧编解码 + 能力描述符模型 + 流式 `FrameParser`（传输无关） |
| `eva/transport/` | **已实现** | `StreamTransport` 成帧基类；`SocketTransport`（测试/未来 TCP）、`SerialTransport`（USB/UART，pyserial 延迟导入） |
| `eva/core/` | **已实现** | `Module`/`RemoteModule` + `ModuleManager`（发现/注册/路由/遥测） |
| `eva/sim/` | **已实现** | `BaseModuleSimulator`：无硬件模拟模块1底座 |
| `eva/modules/` | 占位 | `CameraModule`/`MicModule`/`SpeakerModule` 见阶段1 |
| `eva/config/` | 占位 | 串口/引脚/地址配置 |

## 无硬件验证（仅标准库，无需第三方依赖或任何硬件）

```bash
cd brain
python -m eva.protocol                  # 协议 round-trip + CRC 自测
python -m eva.sim                        # 端到端演示：大脑↔模拟底座 发现/命令/遥测
python -m unittest discover -s tests -v  # 全部单元测试
```

## 板子到货后切到真实硬件

把演示/编排里的 `SocketTransport` 换成 `SerialTransport("/dev/ttyACM0")` 即可，
其余（成帧、ModuleManager、模块代理）一行不用改——`BaseModuleSimulator` 由真实
`firmware/modules/module1_base` 固件替代。无硬件想先验证串口路径，可用 `socat` 造一对虚拟串口
（见 `eva/transport/serial.py` 顶部说明）。

## 阶段1 依赖（届时在树莓派安装）

`pyserial`（串口）、`opencv-python`/`picamera2`（摄像头）、`sounddevice`/`numpy`（音频）。
见 `pyproject.toml` 的 `stage1` optional 分组。
