# cad — 3D 可打印模型

外壳、支架与模块间机械对接件（EVA Mount）。机械接口规范见 [`../docs/module-interface.md`](../docs/module-interface.md)。

## 约定

- **每个模块一个子目录**：`cad/<module_type>/`。
- **源文件入库，导出件不入库**：保留 CAD 源（如 `.FCStd`/`.step`/`.scad`）；`.stl`/`.gcode`/`.3mf`
  为生成产物，已在 `.gitignore` 中忽略——按需本地导出。
- **命名**：`<module>_<part>_v<N>.<ext>`，如 `module1_base_shell_v1.step`。
- **单位**：毫米（mm），右手坐标系，遵循模块接口文档的坐标系约定。

## 状态

阶段0仅定规范；模块1实体建模在阶段1（见 [`module1-base/`](module1-base/)）。
