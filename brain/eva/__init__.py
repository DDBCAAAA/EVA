"""EVA 大脑侧（树莓派）Python 包。

子包：
- protocol: EVA Module Protocol 的帧编解码与消息/能力描述符模型（传输无关）。
- transport: 传输抽象（SerialTransport 等具体实现见阶段1）。
- core:     Module 抽象与 ModuleManager（发现/注册/路由）。
- modules:  具体能力驱动（camera/mic/speaker 本地，电机远程）。
- config:   模块与引脚配置。
"""

__version__ = "0.1.0"
