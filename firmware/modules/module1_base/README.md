# module1_base 固件（占位）

模块1底座控制器（ESP32-S3）的固件。阶段1实现。

## 职责

- 驱动一个电机（类型见 [`../../../docs/hardware-selection.md`](../../../docs/hardware-selection.md) 的"电机类型"）。
- 讲 EVA Module Protocol：`ANNOUNCE`（能力描述符）/ `COMMAND` / `TELEMETRY` / `HEARTBEAT`。
- 预置地址 `0x01`。

## 能力描述符（计划）

```json
{
  "module_type": "module1_base",
  "fw_version": "0.1.0",
  "address": 1,
  "endpoints": [
    {"id": 0, "kind": "actuator", "type": "motor.dc", "name": "base_spin", "unit": "pwm", "range": [-255, 255]}
  ]
}
```

> `type/unit/range` 随最终选定的电机调整（舵机则为 `motor.servo` / `deg` / `[0, 180]` 等）。

引脚见 [`../../../hardware/module1-base/pinmap.md`](../../../hardware/module1-base/pinmap.md)。
