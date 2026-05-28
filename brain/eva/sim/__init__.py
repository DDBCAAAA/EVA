"""无硬件模拟器：在电脑上假装自己是协处理器模块，便于在板子到货前开发与测试大脑侧。

- BaseModuleSimulator：模拟模块1底座（一个电机），讲完整 EVA 协议。

演示（在同一进程里用 socketpair 把大脑接到模拟器）::

    cd brain && python -m eva.sim
"""

from eva.sim.base_module import BaseModuleSimulator, default_base_descriptor

__all__ = ["BaseModuleSimulator", "default_base_descriptor"]
