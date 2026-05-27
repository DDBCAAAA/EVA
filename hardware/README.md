# hardware — 电子

接线图、引脚分配、物料清单。与 `firmware/`（MCU 侧）和 `brain/eva/config/`（Pi 侧引脚）对应。

| 路径 | 说明 |
|------|------|
| [`bom.md`](bom.md) | 物料清单 |
| [`module1-base/pinmap.md`](module1-base/pinmap.md) | 模块1底座引脚分配与接线 |

电源域约定：逻辑 `5V` 与电机 `VBAT` 分离、共地，避免电机噪声干扰 MCU/Pi。
模块连接器引脚规范见 [`../docs/module-interface.md`](../docs/module-interface.md)。
