# 如何新增一个 EVA 模块

一个模块要接入 EVA，需要满足**三层契约**。三者都标准化后，新增模块的工作量就收敛为：
做一块板 + 写一段固件 + 填一份能力描述符。

## 1. 机械契约（EVA Mount）

标准化的对接接口，保证模块之间能稳定固定、对位一致。

- **螺栓孔位**：统一的孔位阵列（待 CAD 阶段定稿，建议 M3、间距固定的矩形阵列）。
- **对位特征**：定位销/凸台，保证装配重复精度。
- **坐标系约定**：每个模块定义自身原点与朝向，遵循右手系；模块装配时其坐标系相对父模块的变换写入该模块文档。
- 对接件为 3D 打印件，源文件与 STL 放在 `cad/<module>/`，命名规范见 `cad/README.md`。

> 当前阶段仅定义规范；实体模型在阶段1及之后建模。

## 2. 电气契约（EVA Connector）

标准化连接器，承载电源与通信总线。引脚定义（待做板定稿）：

| 引脚 | 信号 | 说明 |
|------|------|------|
| 1 | `VBAT` | 主电池电压（如 12V），供电机等大功率负载 |
| 2 | `GND`  | 共地 |
| 3 | `5V`   | 逻辑/外设电源 |
| 4 | `GND`  | 共地 |
| 5 | `BUS_A` | 通信线 A（UART TX / 未来 RS-485 A / CAN_H） |
| 6 | `BUS_B` | 通信线 B（UART RX / 未来 RS-485 B / CAN_L） |

- **模块1最简形态**：树莓派 USB 直连 ESP32，不需要做这个连接器；上表是为多模块总线阶段预留的统一规范。
- 电源域分离：逻辑 `5V` 与电机 `VBAT` 分开，避免电机噪声干扰 MCU/Pi。

## 3. 软件契约（EVA Module Protocol）

模块的协处理器固件必须：

1. 上电后能响应 `DISCOVER`，并以 `ANNOUNCE` 上报**能力描述符**（见 [`module-protocol.md`](module-protocol.md)）。
2. 正确解析发给本地址的 `COMMAND`，对每个 `endpoint_id` 执行相应动作。
3. 按需以 `TELEMETRY` 上报传感器/状态，周期发送 `HEARTBEAT`。
4. 复用 `firmware/lib/eva_protocol/` 的协议常量，保证与大脑侧 `brain/eva/protocol/` 一致。

大脑侧**通常无需改动核心代码**：`ModuleManager` 依据能力描述符自动生成访问代理。
仅当模块需要专门的高层行为（如手臂的逆运动学）时，才在 `brain/eva/modules/` 增加一个高层驱动。

## 新增模块清单（checklist）

- [ ] 在 `firmware/modules/<module_type>/` 写固件，复用 `lib/eva_protocol`。
- [ ] 确定 `module_type` 字符串与各 endpoint 的 `id/kind/type/unit/range`。
- [ ] 机械对接件放入 `cad/<module_type>/`。
- [ ] 接线与引脚记入 `hardware/<module_type>/`，物料补进 `hardware/bom.md`。
- [ ] 若需高层行为，在 `brain/eva/modules/` 加驱动；否则靠自动代理即可。
- [ ] 在 `docs/roadmap.md` 标注模块状态。
