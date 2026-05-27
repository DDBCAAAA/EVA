"""具体能力驱动（阶段1实现）。

规划：
- CameraModule (LocalModule)  —— picamera2 / OpenCV 采集，直挂 Pi。
- MicModule    (LocalModule)  —— I2S/USB 麦克风音频输入。
- SpeakerModule(LocalModule)  —— I2S/USB 扬声器音频输出。
- 电机          —— 不在此实现：作为 RemoteModule 由 ModuleManager 依能力描述符自动构建，
                   仅当需要高层行为（如轨迹/逆运动学）时才在此追加驱动。

本阶段为占位，仅声明规划，不含实现。
"""
