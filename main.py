#!/usr/bin/env python3
"""
俄罗斯方块游戏 - Advanced Tetris
一个功能丰富的桌面俄罗斯方块游戏

作者: Tetris Developer
版本: 1.0.0
"""

import sys
import os

# 添加游戏模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.engine import GameEngine

def main():
    """主函数"""
    try:
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("\n游戏被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"游戏运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()