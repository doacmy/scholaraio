---
name: openfoam
description: Run computational fluid dynamics simulations with OpenFOAM. Covers mesh generation (blockMesh/snappyHexMesh), case setup (boundary conditions, turbulence models, numerical schemes), solver execution, post-processing, and ParaView visualization. Use when the user wants to simulate fluid flow, heat transfer, aerodynamics, or combustion.
version: 1.0.0
author: ZimoLiao/scholaraio
license: MIT
tags: ["scientific-computing", "cfd", "openfoam", "fluid-mechanics", "aerodynamics"]
---

# OpenFOAM 计算流体力学

用 OpenFOAM 做 CFD：从 case 结构、网格、求解器、湍流模型到后处理和验证。

本 skill **故意保持轻量**：
- 它负责告诉 agent 什么时候该用 OpenFOAM、标准工作流是什么、哪些 CFD 规范不能忽略
- 它**不**充当完整字典/求解器手册
- 具体求解器页面、字典字段、模型说明统一去查 `scholaraio toolref`

## 前置条件

```bash
# 安装（Ubuntu/WSL2）
sudo apt install openfoam
# 或 Docker
docker pull openfoam/openfoam-dev

# 可视化
sudo apt install paraview
```

验证：`simpleFoam -help` 应正常输出。确认 `$WM_PROJECT_DIR` 环境变量已设置。

## 何时使用

适合：
- 外流、内流、传热、稳态/瞬态 RANS 或更复杂的 CFD 工作流
- 需要几何建模、网格控制、边界条件和场量后处理的工程问题

不适合：
- 只需要快速低保真估算、且不打算做网格无关性和验证时
- 物理模型选择没有依据、只想“先跑起来再说”的情况

## Toolref 优先

当 agent 不确定求解器、字典、function object、湍流模型时，**先查 toolref**。

常用查法：

```bash
scholaraio toolref show openfoam simpleFoam
scholaraio toolref show openfoam pimpleFoam
scholaraio toolref show openfoam fvSchemes
scholaraio toolref show openfoam fvSolution
scholaraio toolref show openfoam kOmegaSST
scholaraio toolref search openfoam turbulence model
```

推荐习惯：
- 写 case 前先查求解器页面
- 改 `fvSchemes` / `fvSolution` 前先看官方字典说明
- 讨论湍流模型时优先查官方模型页，而不是凭论坛记忆

## 核心工作流

### 知识库协作模式

1. 用 `scholaraio usearch "<流动问题>"` 检索相关论文
2. 从论文提取：几何参数、流动条件（Re, Ma）、湍流模型选择依据、验证数据
3. Case 设置中标注参数来源
4. 计算完成后与实验/DNS 数据定量对比（速度剖面、阻力系数、压力分布）

建议工作流：
1. 读论文/实验资料，确定几何、Re、边界条件、验证指标
2. 选求解器和湍流模型
3. 建网格并做质量检查
4. 配置 `controlDict / fvSchemes / fvSolution`
5. 跑小规模 smoke case 看是否发散
6. 做正式计算
7. 检查残差、力系数、剖面和 y+
8. 与实验 / DNS / 文献做定量对比

### 求解器选择

| 求解器 | 适用场景 |
|--------|---------|
| `simpleFoam` | 稳态不可压 RANS |
| `pimpleFoam` | 瞬态不可压（LES/URANS） |
| `rhoSimpleFoam` | 稳态可压 |
| `sonicFoam` | 瞬态可压/超声速 |
| `buoyantSimpleFoam` | 自然对流/传热 |
| `interFoam` | 两相流（VOF） |
| `reactingFoam` | 燃烧/反应流 |

### 湍流模型

| 模型 | 适用场景 | 何时选用 |
|------|---------|---------|
| `kOmegaSST` | **默认首选**，外流/分离流 | 大多数工程问题 |
| `kEpsilon` | 内流/充分发展流 | 管道、通道 |
| `SpalartAllmaras` | 航空外流 | 翼型、薄边界层 |
| `kOmegaSSTLM` | 转捩流动 | 低 Re 翼型 |
| `Smagorinsky` / `WALE` | LES 亚格子模型 | 需要瞬态细节时 |

**科学规范：湍流模型选择必须有文献依据或物理论证。不能"试了几个选最好看的"。**

### 重点查询点

- `simpleFoam` / `pimpleFoam` / `rhoSimpleFoam` 的适用边界
- `fvSchemes` 和 `fvSolution` 的关键项
- `kOmegaSST` 等湍流模型的物理假设
- `function objects`、`forces`、`yPlus` 的用法

这些细节优先查 `toolref`，不要在 skill 里硬背。

## ParaView 可视化

```python
# pvpython 自动化脚本
from paraview.simple import *

# 加载 OpenFOAM case
reader = OpenFOAMReader(FileName="<case>/case.foam")
reader.UpdatePipeline()

# 表面压力云图
display = Show(reader)
display.SetRepresentationType("Surface")
ColorBy(display, ("CELLS", "p"))
pLUT = GetColorTransferFunction("p")
pLUT.ApplyPreset("Cool to Warm", True)

# 切面
slice = Slice(reader)
slice.SliceType.Normal = [0, 1, 0]  # y=0 对称面
Show(slice)
ColorBy(GetDisplayProperties(slice), ("CELLS", "U", "Magnitude"))

# 渲染
view = GetActiveView()
view.ViewSize = [3840, 2160]
SaveScreenshot("pressure_surface.png", view)
```

## 科学规范

| 检查项 | 正确做法 | 常见错误 |
|--------|---------|---------|
| 网格无关性 | 至少跑粗/中/细三套网格 | 只用一套网格 |
| y+ | 检查并确认在壁面函数范围内 | 不检查 y+ |
| 收敛 | 残差降 3-4 个量级 + 力系数稳定 | 只看残差不看积分量 |
| 域大小 | 出口距物体 >5-8L | 域太小影响尾流 |
| 迎风格式 | linearUpwind（二阶） | 全用一阶迎风（数值耗散过大） |
| 验证 | 与实验/DNS 数据逐点对比 | "看起来对"就算验证 |

## Agent 行为准则

- 不要凭感觉选求解器或湍流模型，先查 `toolref` 并说明依据
- 不要只盯残差，必须同时看积分量、剖面和 y+
- 不要把“收敛了”当“正确了”，验证必须回到实验或基准算例
- 不要把 OpenFOAM 当配置文件游戏，结果解释必须回到流体力学
