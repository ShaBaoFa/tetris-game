# 俄罗斯方块 - Advanced Tetris

[![Python](https://img.shields.io/badge/Python-3.10%2B-29f2d0?style=flat-square)](#)
[![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-ffb347?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/Platform-Windows-5aa9ff?style=flat-square)](#)

Neon 风格桌面俄罗斯方块，强调节奏、策略与可视化反馈。支持高分榜、统计数据、动态加速、幽灵方块与可选音效系统。

在线页面：https://shabaofa.github.io/tetris-game/

## 功能亮点

- 主菜单（开始 / 高分榜 / 统计 / 设置）
- 高分榜持久化（`data/highscores.json`）
- 统计数据（`data/statistics.json`）
- 难度设置与速度提升
- 幽灵方块显示
- 音效系统（可选资源）

## 运行环境

- Python 3.10+
- Windows（已在 Win32 环境测试）

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 控制方式

| 动作 | 按键 |
| --- | --- |
| 移动 | ← / → |
| 旋转 | ↑ |
| 软降 | ↓ |
| 硬降 | Space |
| 暂停 | P |
| 返回菜单 | ESC |

## 数据与存档

- 高分榜：`data/highscores.json`
- 统计数据：`data/statistics.json`

## 音频资源

将音效文件放入 `assets/sounds/` 目录即可启用：

- move.wav
- rotate.wav
- drop.wav
- line.wav
- game_over.wav
- bgm.ogg

如果文件不存在，游戏会自动跳过音效加载。

## 打包为可执行文件（Windows）

```bash
pyinstaller --onefile --windowed main.py
```

或直接运行：

```bash
build_exe.bat
```

生成的可执行文件位于 `dist/` 目录。
