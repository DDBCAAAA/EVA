# EVA Module Protocol 规范

大脑与协处理器模块之间的通信协议。**传输无关**：底层可以是 UART（模块1）、RS-485 或 CAN（多模块），上层语义不变。

参考实现：`brain/eva/protocol/`（Python）；固件侧常量镜像在 `firmware/lib/eva_protocol/`。

## 帧格式

```
+-----+-----+-----+-----+------+-----+-----+----------------+--------+
| SOF | VER | SRC | DST | TYPE | SEQ | LEN |   PAYLOAD[LEN]  | CRC16 |
+-----+-----+-----+-----+------+-----+-----+----------------+--------+
  1B    1B    1B    1B    1B     1B    1B      0..255 B        2B
```

| 字段 | 长度 | 说明 |
|------|------|------|
| SOF  | 1B | 起始字节，固定 `0x7E` |
| VER  | 1B | 协议版本，当前 `0x01` |
| SRC  | 1B | 源地址 |
| DST  | 1B | 目的地址 |
| TYPE | 1B | 消息类型（见下） |
| SEQ  | 1B | 序列号，用于匹配 ACK / 去重，逐帧自增回绕 |
| LEN  | 1B | PAYLOAD 字节数（0–255） |
| PAYLOAD | LEN B | 负载，按 TYPE 解释 |
| CRC16 | 2B | 对 `VER..PAYLOAD`（不含 SOF）做 CRC-16/CCITT-FALSE，小端 |

- **字节序**：多字节数值字段一律小端（little-endian）。
- **成帧/转义**：当前 UART 点对点阶段，接收端以 SOF 对齐、按 LEN 读满、校验 CRC；若 CRC 失败则丢弃并重新寻找下一个 SOF。迁移到总线时如需透明传输再引入 SOF 转义（保留 `0x7D` 作为转义前缀），届时升 VER。

## 地址分配

| 地址 | 含义 |
|------|------|
| `0x00` | 大脑（Brain） |
| `0x01`–`0xFE` | 模块（上电由大脑分配或固件预置） |
| `0xFF` | 广播 |

模块1：底座 ESP32 预置为 `0x01`。多模块阶段可在 DISCOVER 流程中由大脑动态分配。

## 消息类型

| TYPE | 名称 | 方向 | PAYLOAD |
|------|------|------|---------|
| `0x01` | `ANNOUNCE`  | 模块→大脑 | 能力描述符（见下） |
| `0x02` | `DISCOVER`  | 大脑→广播 | 空 |
| `0x03` | `COMMAND`   | 大脑→模块 | `endpoint_id(1B)` + 命令参数 |
| `0x04` | `TELEMETRY` | 模块→大脑 | `endpoint_id(1B)` + 传感器/状态数据 |
| `0x05` | `HEARTBEAT` | 双向 | 空（或 1B 状态标志） |
| `0x06` | `ACK`       | 双向 | `acked_seq(1B)` |
| `0x07` | `ERROR`     | 双向 | `code(1B)` + UTF-8 文本 |

### 典型时序

```
大脑                          模块(ESP32 底座)
 |---- DISCOVER (broadcast) -->|
 |<--- ANNOUNCE (能力描述符) --|     (模块上电也可主动 ANNOUNCE)
 |                             |
 |---- COMMAND  (设定电机) --->|
 |<--- ACK ------------------- |
 |<--- TELEMETRY (电机状态) ---|     (周期或事件上报)
 |<--- HEARTBEAT ------------- |     (周期保活；超时判离线)
```

## 能力描述符（即插即用的核心）

`ANNOUNCE` 的 PAYLOAD 是一段紧凑的能力描述符，让大脑无需硬编码即可理解一个模块。
当前用 **JSON**（UTF-8）以便开发期可读；负载偏大时可在不改语义的前提下切到 CBOR（升 VER）。

字段：

```json
{
  "module_type": "module1_base",
  "fw_version": "0.1.0",
  "address": 1,
  "endpoints": [
    {
      "id": 0,
      "kind": "actuator",
      "type": "motor.dc",
      "name": "base_spin",
      "unit": "pwm",
      "range": [-255, 255]
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `module_type` | 模块类型标识，对应 `firmware/modules/<type>` |
| `fw_version`  | 固件语义化版本 |
| `address`     | 模块当前地址 |
| `endpoints[]` | 该模块暴露的执行器/传感器端点 |
| `endpoints[].id`    | 模块内端点编号，`COMMAND/TELEMETRY` 用它寻址 |
| `endpoints[].kind`  | `actuator` 或 `sensor` |
| `endpoints[].type`  | 端点子类型，如 `motor.dc` / `motor.servo` / `sensor.encoder` |
| `endpoints[].name`  | 人类可读名 |
| `endpoints[].unit`  | 物理/逻辑单位 |
| `endpoints[].range` | 合法取值范围 `[min, max]` |

大脑收到后，为每个 endpoint 生成对应的访问代理（actuator → 可下发 COMMAND；sensor → 订阅 TELEMETRY）。

## 版本与兼容

- `VER` 字段标识帧层版本。任何破坏性变更（成帧、字段含义、描述符编码）都必须递增 `VER`。
- 端点 `type` 命名采用 `domain.subtype` 约定，新增子类型不需改协议层。

## 错误码（ERROR）

| code | 含义 |
|------|------|
| `0x01` | CRC 校验失败（接收端可请求重发） |
| `0x02` | 未知 TYPE |
| `0x03` | 未知 endpoint_id |
| `0x04` | 参数越界 |
| `0x05` | 模块忙 / 暂不可用 |
