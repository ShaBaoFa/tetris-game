# Advanced Tetris

[![Python](https://img.shields.io/badge/Python-3.10%2B-29f2d0?style=flat-square)](#)
[![Pygame](https://img.shields.io/badge/Pygame-2.6%2B-ffb347?style=flat-square)](#)
[![Platform](https://img.shields.io/badge/Platform-Windows-5aa9ff?style=flat-square)](#)

[中文](#中文) | [English](#english) | [日本語](#日本語)

## 中文

Neon 风格桌面俄罗斯方块，强调节奏、策略与可视化反馈。支持高分榜、统计数据、动态加速、幽灵方块与可选音效系统。

- 在线页面：https://shabaofa.github.io/tetris-game/
- Windows 可执行版：https://github.com/ShaBaoFa/tetris-game/releases/latest

### 运行环境

- Python 3.10+
- Windows（已在 Win32 环境测试）

### 快速开始

```bash
pip install -r requirements.txt
python main.py
```

### 控制方式

| 动作 | 按键 |
| --- | --- |
| 移动 | ← / → |
| 旋转 | ↑ |
| 软降 | ↓ |
| 硬降 | Space |
| 暂停 | P |
| 返回菜单 | ESC |

### 功能亮点

- 主菜单（开始 / 高分榜 / 统计 / 设置）
- 高分榜持久化（`data/highscores.json`）
- 统计数据（`data/statistics.json`）
- 难度设置与速度提升
- 幽灵方块显示
- 音效系统（可选资源）
- 语言切换（中文 / English / 日本語）

### 数据与存档

- 高分榜：`data/highscores.json`
- 统计数据：`data/statistics.json`

### 音频资源

将音效文件放入 `assets/sounds/` 目录即可启用：

- move.wav
- rotate.wav
- drop.wav
- line.wav
- game_over.wav
- bgm.ogg

如果文件不存在，游戏会自动跳过音效加载。

### 打包为可执行文件（Windows）

```bash
pyinstaller main.spec
```

项目已配置 GitHub Actions，可在 Releases 中获取自动打包的可执行文件。

## English

Neon-styled desktop Tetris focused on rhythm, strategy, and clarity. Includes high scores, stats, dynamic speed, ghost piece, and optional audio.

- Live page: https://shabaofa.github.io/tetris-game/
- Windows executable: https://github.com/ShaBaoFa/tetris-game/releases/latest

### Requirements

- Python 3.10+
- Windows (tested on Win32)

### Quick Start

```bash
pip install -r requirements.txt
python main.py
```

### Controls

| Action | Key |
| --- | --- |
| Move | ← / → |
| Rotate | ↑ |
| Soft drop | ↓ |
| Hard drop | Space |
| Pause | P |
| Back to menu | ESC |

### Features

- Main menu (Start / High Scores / Statistics / Settings)
- Persistent high scores (`data/highscores.json`)
- Stats tracking (`data/statistics.json`)
- Difficulty tuning and speed ramp
- Ghost piece
- Optional audio pack
- Language switching (中文 / English / 日本語)

### Data

- High scores: `data/highscores.json`
- Statistics: `data/statistics.json`

### Audio

Drop audio files into `assets/sounds/`:

- move.wav
- rotate.wav
- drop.wav
- line.wav
- game_over.wav
- bgm.ogg

Missing files are skipped automatically.

### Build (Windows)

```bash
pyinstaller main.spec
```

GitHub Actions builds releases automatically.

## 日本語

リズムと戦略性を重視した Neon スタイルのデスクトップ版テトリス。ハイスコア、統計、動的スピード、ゴースト表示、音声に対応。

- ライブページ：https://shabaofa.github.io/tetris-game/
- Windows 実行ファイル：https://github.com/ShaBaoFa/tetris-game/releases/latest

### 動作環境

- Python 3.10+
- Windows（Win32 で動作確認）

### 起動方法

```bash
pip install -r requirements.txt
python main.py
```

### 操作方法

| 操作 | キー |
| --- | --- |
| 移動 | ← / → |
| 回転 | ↑ |
| ソフトドロップ | ↓ |
| ハードドロップ | Space |
| 一時停止 | P |
| メニューへ戻る | ESC |

### 特徴

- メインメニュー（開始 / ハイスコア / 統計 / 設定）
- ハイスコア保存（`data/highscores.json`）
- 統計データ（`data/statistics.json`）
- 難易度とスピード調整
- ゴースト表示
- 音声（任意）
- 言語切替（中文 / English / 日本語）

### データ

- ハイスコア：`data/highscores.json`
- 統計：`data/statistics.json`

### 音声

`assets/sounds/` に配置：

- move.wav
- rotate.wav
- drop.wav
- line.wav
- game_over.wav
- bgm.ogg

未配置の場合は自動的にスキップされます。

### ビルド（Windows）

```bash
pyinstaller main.spec
```

GitHub Actions がリリース用実行ファイルを自動生成します。
