"""核心层：Module 抽象与 ModuleManager（发现/注册/路由）。"""

from eva.core.module import Module, LocalModule, RemoteModule
from eva.core.manager import ModuleManager

__all__ = ["Module", "LocalModule", "RemoteModule", "ModuleManager"]
