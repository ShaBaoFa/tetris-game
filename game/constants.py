# 游戏常量配置
import pygame

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
FPS = 60

# 颜色定义
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'GRAY': (128, 128, 128),
    'DARK_GRAY': (64, 64, 64),
    'LIGHT_GRAY': (192, 192, 192),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'CYAN': (0, 255, 255),
    'MAGENTA': (255, 0, 255),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
    'PINK': (255, 192, 203)
}

# 俄罗斯方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],           # I
    [[1, 1], [1, 1]],         # O
    [[1, 1, 1], [0, 1, 0]],   # T
    [[0, 1, 1], [1, 1, 0]],   # S
    [[1, 1, 0], [0, 1, 1]],   # Z
    [[1, 0, 0], [1, 1, 1]],   # J
    [[0, 0, 1], [1, 1, 1]]    # L
]

# 方块颜色
PIECE_COLORS = [COLORS['CYAN'], COLORS['YELLOW'], COLORS['MAGENTA'], 
                COLORS['GREEN'], COLORS['RED'], COLORS['BLUE'], COLORS['ORANGE']]

# 游戏难度设置
DIFFICULTY_SETTINGS = {
    'EASY': {'fall_speed': 0.8, 'score_multiplier': 1.0},
    'MEDIUM': {'fall_speed': 0.5, 'score_multiplier': 1.5},
    'HARD': {'fall_speed': 0.3, 'score_multiplier': 2.0},
    'EXPERT': {'fall_speed': 0.15, 'score_multiplier': 3.0}
}

# 主题设置
THEMES = {
    'CLASSIC': {
        'background': COLORS['BLACK'],
        'border': COLORS['GRAY'],
        'text': COLORS['WHITE'],
        'muted_text': COLORS['LIGHT_GRAY'],
        'ghost': COLORS['DARK_GRAY']
    },
    'NEON': {
        'background': (8, 10, 28),
        'border': (0, 255, 204),
        'text': (220, 255, 255),
        'muted_text': (120, 200, 200),
        'ghost': (0, 150, 140)
    },
    'PASTEL': {
        'background': (20, 20, 24),
        'border': (200, 180, 220),
        'text': (250, 240, 255),
        'muted_text': (180, 170, 200),
        'ghost': (120, 120, 140)
    }
}

# 得分规则
SCORE_RULES = {
    'SINGLE': 100,
    'DOUBLE': 300,
    'TRIPLE': 500,
    'TETRIS': 800,
    'SOFT_DROP': 1,
    'HARD_DROP': 2
}
