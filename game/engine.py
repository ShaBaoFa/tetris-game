import pygame
import sys
import time
import os
from .constants import *
from .tetris import GameBoard, Tetromino
from .highscore import HighScoreManager
from .statistics import StatisticsManager
from .settings import SettingsManager
from .sound import SoundManager
from .i18n import (
    t,
    format_time,
    difficulty_label,
    theme_label,
    LANGUAGE_LABELS,
    LANGUAGE_ORDER,
)

class GameEngine:
    """游戏引擎类"""
    
    def __init__(self):
        """初始化游戏引擎"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.font = self._load_font(30)
        self.small_font = self._load_font(20)
        self.tiny_font = self._load_font(16)
        
        # 数据管理器
        self.high_score_manager = HighScoreManager()
        self.stats_manager = StatisticsManager()
        self.settings_manager = SettingsManager()
        self.sound_manager = SoundManager(self.base_dir, self.settings_manager)
        self.theme = THEMES.get(self.settings_manager.get_setting('theme', 'CLASSIC'), THEMES['CLASSIC'])
        self.language = self.settings_manager.get_setting('language', 'zh')
        pygame.display.set_caption(t(self.language, "app.title"))
        
        # 游戏状态
        self.board = GameBoard()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.difficulty = self.settings_manager.get_setting('difficulty', 'MEDIUM')
        
        # 时间控制
        self.fall_time = 0
        self.fall_speed = DIFFICULTY_SETTINGS[self.difficulty]['fall_speed']
        self.last_fall_time = time.time()
        self.game_start_time = None
        self.current_session_time = 0
        
        # 游戏状态
        self.game_state = 'MENU'  # MENU, PLAYING, PAUSED, GAME_OVER, HIGH_SCORES, STATISTICS
        
        # 菜单状态
        self.menu_index = 0
        self.menu_item_keys = [
            'menu.start',
            'menu.high_scores',
            'menu.statistics',
            'menu.settings',
            'menu.exit'
        ]
        self.menu_items = []
        self._update_menu_items()
        
        # 设置菜单状态
        self.settings_menu_index = 0
        self.settings_menu_entries = []
        self._update_settings_menu()
        
        # 输入状态
        self.entering_name = False
        self.player_name = ""
        
        # 初始化游戏
        self.board.create_new_piece()

    def _t(self, key: str, **kwargs) -> str:
        return t(self.language, key, **kwargs)

    def _on_off(self, value: bool) -> str:
        return self._t('toggle.on') if value else self._t('toggle.off')

    def _update_menu_items(self) -> None:
        self.menu_items = [self._t(key) for key in self.menu_item_keys]

    def _cycle_language(self, direction: int) -> None:
        if self.language not in LANGUAGE_ORDER:
            self.language = 'en'
        current_index = LANGUAGE_ORDER.index(self.language)
        next_index = (current_index + direction) % len(LANGUAGE_ORDER)
        self.language = LANGUAGE_ORDER[next_index]
        self.settings_manager.set_setting('language', self.language)
        pygame.display.set_caption(self._t('app.title'))
        self._update_menu_items()
        self._update_settings_menu()
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == 'MENU':
                    self._handle_menu_input(event.key, event)
                elif self.game_state == 'PLAYING':
                    self._handle_game_input(event.key)
                elif self.game_state == 'PAUSED':
                    self._handle_pause_input(event.key)
                elif self.game_state == 'GAME_OVER':
                    self._handle_game_over_input(event.key)
                elif self.game_state == 'HIGH_SCORE_ENTRY':
                    self._handle_high_score_entry_input(event.key, event)
                elif self.game_state in ['HIGH_SCORES', 'STATISTICS']:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'MENU'
                elif self.game_state == 'SETTINGS':
                    self._handle_settings_input(event.key)
                        
        return True
    
    def _handle_high_score_entry_input(self, key, event):
        """处理高分输入"""
        if key == pygame.K_RETURN and self.player_name.strip():
            # 保存高分
            self.high_score_manager.add_score(
                self.player_name,
                int(self.score),
                self.level,
                self.lines_cleared,
                default_name=self._t('default_player_name')
            )
            self.player_name = ""
            self.entering_name = False
            self.game_state = 'MENU'
        elif key == pygame.K_ESCAPE:
            self.player_name = ""
            self.entering_name = False
            self.game_state = 'MENU'
        elif key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        else:
            if len(self.player_name) < 15:  # 限制姓名长度
                self.player_name += event.unicode if hasattr(event, 'unicode') and event.unicode.isprintable() else ''
    
    def _handle_menu_input(self, key, event):
        """处理菜单输入"""
        if self.entering_name:
            # 输入玩家姓名
            if key == pygame.K_RETURN and self.player_name.strip():
                # 保存高分
                self.high_score_manager.add_score(
                    self.player_name,
                    int(self.score),
                    self.level,
                    self.lines_cleared,
                    default_name=self._t('default_player_name')
                )
                self.player_name = ""
                self.entering_name = False
                self.game_state = 'MENU'
            elif key == pygame.K_ESCAPE:
                self.player_name = ""
                self.entering_name = False
                self.game_state = 'MENU'
            elif key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                if len(self.player_name) < 15:  # 限制姓名长度
                    self.player_name += event.unicode if hasattr(event, 'unicode') else ''
        else:
            if key == pygame.K_UP:
                self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            elif key == pygame.K_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            elif key == pygame.K_RETURN:
                self._execute_menu_item()
            elif key == pygame.K_ESCAPE:
                return False
            
    def _handle_game_input(self, key):
        """处理游戏输入"""
        if key == pygame.K_LEFT:
            if self.board.move_piece(-1, 0):
                self.sound_manager.play_sound('move')
        elif key == pygame.K_RIGHT:
            if self.board.move_piece(1, 0):
                self.sound_manager.play_sound('move')
        elif key == pygame.K_DOWN:
            if self.board.move_piece(0, 1):
                self.score += SCORE_RULES['SOFT_DROP']
                self.sound_manager.play_sound('move')
        elif key == pygame.K_UP:
            if self.board.rotate_piece():
                self.sound_manager.play_sound('rotate')
        elif key == pygame.K_SPACE:
            # 硬降
            while self.board.move_piece(0, 1):
                self.score += SCORE_RULES['HARD_DROP']
            self.sound_manager.play_sound('drop')
            self._lock_current_piece()
        elif key == pygame.K_p:
            self.game_state = 'PAUSED'
        elif key == pygame.K_ESCAPE:
            self.game_state = 'MENU'
            
    def _handle_pause_input(self, key):
        """处理暂停输入"""
        if key == pygame.K_p:
            self.game_state = 'PLAYING'
        elif key == pygame.K_ESCAPE:
            self.game_state = 'MENU'
            
    def _handle_game_over_input(self, key):
        """处理游戏结束输入"""
        if key == pygame.K_SPACE:
            # 检查是否为高分
            if self.high_score_manager.is_high_score(int(self.score)):
                self.entering_name = True
                self.player_name = ""
                self.game_state = 'HIGH_SCORE_ENTRY'
            else:
                self.start_new_game()
        elif key == pygame.K_ESCAPE:
            self.game_state = 'MENU'
            
    def _execute_menu_item(self):
        """执行菜单项"""
        item_key = self.menu_item_keys[self.menu_index]
        
        if item_key == 'menu.start':
            self.start_new_game()
        elif item_key == 'menu.high_scores':
            self.game_state = 'HIGH_SCORES'
        elif item_key == 'menu.statistics':
            self.game_state = 'STATISTICS'
        elif item_key == 'menu.settings':
            self.game_state = 'SETTINGS'
            self._update_settings_menu()
        elif item_key == 'menu.exit':
            pygame.quit()
            sys.exit()
            
    def update(self):
        """更新游戏状态"""
        if self.game_state != 'PLAYING':
            return
            
        current_time = time.time()
        
        # 方块自动下落
        if current_time - self.last_fall_time > self.fall_speed:
            if not self.board.move_piece(0, 1):
                self._lock_current_piece()
            self.last_fall_time = current_time
            
    def _lock_current_piece(self):
        """锁定当前方块"""
        lines_cleared = self.board.lock_piece()
        
        if lines_cleared > 0:
            self._calculate_score(lines_cleared)
            self.lines_cleared += lines_cleared
            self.sound_manager.play_sound('line')
            
            # 更新等级
            self.level = self.lines_cleared // 10 + 1
            self._update_fall_speed()
        
        # 创建新方块
        if not self.board.create_new_piece():
            self.game_over = True
            self.game_state = 'GAME_OVER'
            self.sound_manager.play_sound('game_over')
            
            # 记录游戏统计
            if self.game_start_time:
                session_time = time.time() - self.game_start_time
                self.stats_manager.record_game(
                    int(self.score), self.level, self.lines_cleared, self.difficulty
                )
                self.stats_manager.end_session(session_time)
                self.game_start_time = None
            
    def _calculate_score(self, lines_cleared):
        """计算得分"""
        score_multiplier = DIFFICULTY_SETTINGS[self.difficulty]['score_multiplier']
        
        if lines_cleared == 1:
            self.score += SCORE_RULES['SINGLE'] * self.level * score_multiplier
        elif lines_cleared == 2:
            self.score += SCORE_RULES['DOUBLE'] * self.level * score_multiplier
        elif lines_cleared == 3:
            self.score += SCORE_RULES['TRIPLE'] * self.level * score_multiplier
        elif lines_cleared == 4:
            self.score += SCORE_RULES['TETRIS'] * self.level * score_multiplier

    def _load_font(self, size):
        """加载支持中文的字体"""
        # 优先加载项目内字体文件
        fonts_dir = os.path.join(self.base_dir, 'assets', 'fonts')
        font_candidates = [
            os.path.join(fonts_dir, 'NotoSansSC-Regular.ttf'),
            os.path.join(fonts_dir, 'SourceHanSansCN-Regular.otf'),
            os.path.join(fonts_dir, 'msyh.ttc')
        ]
        for path in font_candidates:
            if os.path.exists(path):
                try:
                    return pygame.font.Font(path, size)
                except pygame.error:
                    pass

        # 系统字体回退
        system_fonts = [
            'Microsoft YaHei',
            'Microsoft YaHei UI',
            'SimHei',
            'SimSun',
            'PingFang SC',
            'WenQuanYi Zen Hei'
        ]
        for name in system_fonts:
            if pygame.font.match_font(name):
                return pygame.font.SysFont(name, size)

        return pygame.font.Font(None, size)
    
    def _update_fall_speed(self):
        """更新下落速度"""
        base_speed = DIFFICULTY_SETTINGS[self.difficulty]['fall_speed']
        speed_increase = 0.05 * (self.level - 1)
        self.fall_speed = max(base_speed - speed_increase, 0.05)
    
    def start_new_game(self):
        """开始新游戏"""
        if self.game_start_time:
            session_time = time.time() - self.game_start_time
            self.stats_manager.end_session(session_time)
        
        self.board.reset()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_speed = DIFFICULTY_SETTINGS[self.difficulty]['fall_speed']
        self.game_state = 'PLAYING'
        self.game_start_time = time.time()
        self.stats_manager.start_session()
        self.board.create_new_piece()
        self.sound_manager.update_settings()
        self.sound_manager.play_music()
    
    def _handle_settings_input(self, key):
        """处理设置菜单输入"""
        if key == pygame.K_UP:
            self.settings_menu_index = (self.settings_menu_index - 1) % len(self.settings_menu_entries)
        elif key == pygame.K_DOWN:
            self.settings_menu_index = (self.settings_menu_index + 1) % len(self.settings_menu_entries)
        elif key == pygame.K_RETURN:
            self._execute_settings_item()
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._adjust_setting(key)
        elif key == pygame.K_ESCAPE:
            self.game_state = 'MENU'
    
    def _execute_settings_item(self):
        """执行设置项"""
        entry_id = self.settings_menu_entries[self.settings_menu_index]['id']
        
        if entry_id == 'difficulty':
            difficulties = ['EASY', 'MEDIUM', 'HARD', 'EXPERT']
            current_index = difficulties.index(self.difficulty)
            next_index = (current_index + 1) % len(difficulties)
            self.difficulty = difficulties[next_index]
            self.settings_manager.set_setting('difficulty', self.difficulty)
        elif entry_id == 'sound':
            current = self.settings_manager.get_setting('sound_enabled', True)
            self.settings_manager.set_setting('sound_enabled', not current)
        elif entry_id == 'music':
            current = self.settings_manager.get_setting('music_enabled', True)
            self.settings_manager.set_setting('music_enabled', not current)
        elif entry_id == 'ghost':
            current = self.settings_manager.get_setting('show_ghost_piece', True)
            self.settings_manager.set_setting('show_ghost_piece', not current)
        elif entry_id == 'theme':
            themes = list(THEMES.keys())
            current = self.settings_manager.get_setting('theme', 'CLASSIC')
            current_index = themes.index(current) if current in themes else 0
            next_index = (current_index + 1) % len(themes)
            self.settings_manager.set_setting('theme', themes[next_index])
            self.theme = THEMES.get(themes[next_index], THEMES['CLASSIC'])
        elif entry_id == 'language':
            self._cycle_language(1)
        elif entry_id == 'reset':
            self.settings_manager.reset_to_default()
            self.difficulty = self.settings_manager.get_setting('difficulty', 'MEDIUM')
            self.theme = THEMES.get(self.settings_manager.get_setting('theme', 'CLASSIC'), THEMES['CLASSIC'])
            self.language = self.settings_manager.get_setting('language', 'zh')
            pygame.display.set_caption(self._t('app.title'))
            self._update_menu_items()
        elif entry_id == 'back':
            self.game_state = 'MENU'

        if entry_id != 'back':
            self._update_settings_menu()

        self.sound_manager.update_settings()
        if self.settings_manager.get_setting('music_enabled', True):
            self.sound_manager.play_music()
        else:
            self.sound_manager.stop_music()
    
    def _adjust_setting(self, key):
        """调整设置值（左右键）"""
        entry_id = self.settings_menu_entries[self.settings_menu_index]['id']
        direction = -1 if key == pygame.K_LEFT else 1
        if entry_id == 'difficulty':
            difficulties = ['EASY', 'MEDIUM', 'HARD', 'EXPERT']
            current_index = difficulties.index(self.difficulty)
            current_index = (current_index + direction) % len(difficulties)
            self.difficulty = difficulties[current_index]
            self.settings_manager.set_setting('difficulty', self.difficulty)
        elif entry_id == 'theme':
            themes = list(THEMES.keys())
            current = self.settings_manager.get_setting('theme', 'CLASSIC')
            current_index = themes.index(current) if current in themes else 0
            current_index = (current_index + direction) % len(themes)
            self.settings_manager.set_setting('theme', themes[current_index])
            self.theme = THEMES.get(themes[current_index], THEMES['CLASSIC'])
        elif entry_id == 'language':
            self._cycle_language(direction)
        elif entry_id in ['sound', 'music', 'ghost']:
            current_key = {
                'sound': 'sound_enabled',
                'music': 'music_enabled',
                'ghost': 'show_ghost_piece'
            }[entry_id]
            current_value = self.settings_manager.get_setting(current_key, True)
            self.settings_manager.set_setting(current_key, not current_value)

        self._update_settings_menu()
    
    def _update_settings_menu(self):
        """更新设置菜单显示"""
        theme_value = self.settings_manager.get_setting('theme', 'CLASSIC')
        self.settings_menu_entries = [
            {
                'id': 'difficulty',
                'label': f"{self._t('settings.difficulty')}: {difficulty_label(self.language, self.difficulty)}"
            },
            {
                'id': 'sound',
                'label': f"{self._t('settings.sound')}: {self._on_off(self.settings_manager.get_setting('sound_enabled', True))}"
            },
            {
                'id': 'music',
                'label': f"{self._t('settings.music')}: {self._on_off(self.settings_manager.get_setting('music_enabled', True))}"
            },
            {
                'id': 'ghost',
                'label': f"{self._t('settings.ghost')}: {self._on_off(self.settings_manager.get_setting('show_ghost_piece', True))}"
            },
            {
                'id': 'theme',
                'label': f"{self._t('settings.theme')}: {theme_label(self.language, theme_value)}"
            },
            {
                'id': 'language',
                'label': f"{self._t('settings.language')}: {LANGUAGE_LABELS.get(self.language, self.language)}"
            },
            {
                'id': 'reset',
                'label': self._t('settings.reset')
            },
            {
                'id': 'back',
                'label': self._t('settings.back')
            }
        ]
        self.settings_menu_index = min(self.settings_menu_index, len(self.settings_menu_entries) - 1)
    
    def render(self):
        """渲染游戏画面"""
        self.theme = THEMES.get(self.settings_manager.get_setting('theme', 'CLASSIC'), THEMES['CLASSIC'])
        self.screen.fill(self.theme['background'])
        
        if self.game_state == 'MENU':
            self._render_menu()
        elif self.game_state == 'PLAYING':
            self._render_game()
        elif self.game_state == 'PAUSED':
            self._render_game()
            self._render_pause_overlay()
        elif self.game_state == 'GAME_OVER':
            self._render_game()
            self._render_game_over_overlay()
        elif self.game_state == 'HIGH_SCORES':
            self._render_high_scores()
        elif self.game_state == 'STATISTICS':
            self._render_statistics()
        elif self.game_state == 'HIGH_SCORE_ENTRY':
            self._render_high_score_entry()
        elif self.game_state == 'SETTINGS':
            self._render_settings()
        
        pygame.display.flip()
    
    def _render_menu(self):
        """渲染菜单"""
        title = self.font.render(self._t('menu.title'), True, COLORS['WHITE'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        for i, item in enumerate(self.menu_items):
            color = COLORS['YELLOW'] if i == self.menu_index else COLORS['WHITE']
            text = self.small_font.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 40))
            self.screen.blit(text, text_rect)
        
        controls = [
            self._t('menu.hint.up_down'),
            self._t('menu.hint.enter'),
            self._t('menu.hint.esc')
        ]
        for i, control in enumerate(controls):
            text = self.tiny_font.render(control, True, COLORS['LIGHT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 450 + i * 20))
            self.screen.blit(text, text_rect)
    
    def _render_game(self):
        """渲染游戏画面"""
        self._render_board()
        
        if self.board.current_piece:
            self._render_piece(self.board.current_piece)
        
        if self.board.ghost_piece and self.settings_manager.get_setting('show_ghost_piece', True):
            self._render_ghost_piece()
        
        self._render_sidebar()
    
    def _render_board(self):
        """渲染游戏板"""
        pygame.draw.rect(self.screen, self.theme['border'],
                         (0, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE), 2)
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board.grid[y][x] > 0:
                    color_index = self.board.grid[y][x] - 1
                    color = PIECE_COLORS[color_index]
                    pygame.draw.rect(self.screen, color,
                                     (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
    
    def _render_piece(self, piece):
        """渲染方块"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece.color,
                                     ((piece.x + x) * GRID_SIZE,
                                      (piece.y + y) * GRID_SIZE,
                                      GRID_SIZE - 1, GRID_SIZE - 1))
    
    def _render_ghost_piece(self):
        """渲染幽灵方块"""
        ghost = self.board.ghost_piece
        if not ghost:
            return
        
        for y, row in enumerate(ghost.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.theme['ghost'],
                                     ((ghost.x + x) * GRID_SIZE,
                                      (ghost.y + y) * GRID_SIZE,
                                      GRID_SIZE - 1, GRID_SIZE - 1), 1)
    
    def _render_sidebar(self):
        """渲染侧边栏"""
        sidebar_x = GRID_WIDTH * GRID_SIZE + 20
        
        next_text = self.small_font.render(self._t('sidebar.next'), True, COLORS['WHITE'])
        self.screen.blit(next_text, (sidebar_x, 20))
        
        if self.board.next_piece:
            for y, row in enumerate(self.board.next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.board.next_piece.color,
                                         (sidebar_x + x * 20, 60 + y * 20, 18, 18))
        
        score_text = self.small_font.render(
            f"{self._t('sidebar.score')}: {int(self.score)}", True, COLORS['WHITE']
        )
        self.screen.blit(score_text, (sidebar_x, 150))
        
        level_text = self.small_font.render(
            f"{self._t('sidebar.level')}: {self.level}", True, COLORS['WHITE']
        )
        self.screen.blit(level_text, (sidebar_x, 180))
        
        lines_text = self.small_font.render(
            f"{self._t('sidebar.lines')}: {self.lines_cleared}", True, COLORS['WHITE']
        )
        self.screen.blit(lines_text, (sidebar_x, 210))
        
        diff_text = self.small_font.render(
            f"{self._t('sidebar.difficulty')}: {difficulty_label(self.language, self.difficulty)}",
            True,
            COLORS['WHITE']
        )
        self.screen.blit(diff_text, (sidebar_x, 240))
        
        controls_y = 320
        controls = [
            self._t('sidebar.controls'),
            self._t('controls.left_right'),
            self._t('controls.rotate'),
            self._t('controls.soft_drop'),
            self._t('controls.hard_drop'),
            self._t('controls.pause'),
            self._t('controls.menu')
        ]
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, COLORS['LIGHT_GRAY'])
            self.screen.blit(control_text, (sidebar_x, controls_y + i * 25))
    
    def _render_pause_overlay(self):
        """渲染暂停覆盖层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['BLACK'])
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render(self._t('pause.title'), True, COLORS['WHITE'])
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.small_font.render(self._t('pause.resume'), True, COLORS['WHITE'])
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(resume_text, resume_rect)
    
    def _render_game_over_overlay(self):
        """渲染游戏结束覆盖层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['BLACK'])
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render(self._t('game_over.title'), True, COLORS['RED'])
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, game_over_rect)
        
        final_score_text = self.small_font.render(
            f"{self._t('game_over.final_score')}: {int(self.score)}",
            True,
            COLORS['WHITE']
        )
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)
        
        restart_text = self.small_font.render(self._t('game_over.continue'), True, COLORS['WHITE'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(restart_text, restart_rect)
        
        menu_text = self.small_font.render(self._t('game_over.menu'), True, COLORS['WHITE'])
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(menu_text, menu_rect)
    
    def _render_high_scores(self):
        """渲染高分榜"""
        title = self.font.render(self._t('high_scores.title'), True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        high_scores = self.high_score_manager.get_high_scores()
        headers = [
            self._t('high_scores.rank'),
            self._t('high_scores.player'),
            self._t('high_scores.score'),
            self._t('high_scores.level'),
            self._t('high_scores.lines'),
            self._t('high_scores.date')
        ]
        x_positions = [150, 220, 320, 400, 470, 550]
        
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, COLORS['LIGHT_GRAY'])
            self.screen.blit(text, (x_positions[i], 120))
        
        for i, score_data in enumerate(high_scores[:10]):
            y = 160 + i * 30
            color = COLORS['YELLOW'] if i == 0 else COLORS['WHITE']
            self.screen.blit(self.small_font.render(f"#{i+1}", True, color), (x_positions[0], y))
            self.screen.blit(self.small_font.render(score_data['name'][:10], True, color), (x_positions[1], y))
            self.screen.blit(self.small_font.render(str(score_data['score']), True, color), (x_positions[2], y))
            self.screen.blit(self.small_font.render(str(score_data['level']), True, color), (x_positions[3], y))
            self.screen.blit(self.small_font.render(str(score_data['lines']), True, color), (x_positions[4], y))
            date_text = self.tiny_font.render(score_data['date'][:10], True, color)
            self.screen.blit(date_text, (x_positions[5], y + 5))
        
        back_text = self.small_font.render(self._t('game_over.menu'), True, COLORS['WHITE'])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(back_text, back_rect)
    
    def _render_statistics(self):
        """渲染统计数据"""
        title = self.font.render(self._t('statistics.title'), True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        stats = self.stats_manager.get_statistics()
        total_time = format_time(self.language, stats['total_play_time_seconds'])
        avg_session = format_time(self.language, stats['average_session_time'])
        stat_items = [
            f"{self._t('statistics.total_games')}: {stats['total_games']}",
            f"{self._t('statistics.total_time')}: {total_time}",
            f"{self._t('statistics.total_lines')}: {stats['total_lines_cleared']}",
            f"{self._t('statistics.total_score')}: {stats['total_score']}",
            f"{self._t('statistics.highest_score')}: {stats['highest_score']}",
            f"{self._t('statistics.highest_level')}: {stats['highest_level']}",
            f"{self._t('statistics.most_lines')}: {stats['most_lines_cleared']}",
            f"{self._t('statistics.average_score')}: {stats['average_score']}",
            f"{self._t('statistics.average_lines')}: {stats['average_lines']}",
            f"{self._t('statistics.average_session')}: {avg_session}"
        ]
        
        y = 120
        for i, stat in enumerate(stat_items):
            text = self.small_font.render(stat, True, COLORS['WHITE'])
            self.screen.blit(text, (200, y + i * 30))
        
        y = 420
        diff_text = self.small_font.render(self._t('statistics.difficulty_distribution'), True, COLORS['LIGHT_GRAY'])
        self.screen.blit(diff_text, (200, y))
        
        difficulty_stats = stats['games_per_difficulty']
        for i, (difficulty, count) in enumerate(difficulty_stats.items()):
            y = 450 + i * 25
            label = difficulty_label(self.language, difficulty)
            text = self.tiny_font.render(
                f"{label}: {count} {self._t('statistics.games_suffix')}",
                True,
                COLORS['WHITE']
            )
            self.screen.blit(text, (220, y))
        
        back_text = self.small_font.render(self._t('game_over.menu'), True, COLORS['WHITE'])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(back_text, back_rect)
    
    def _render_high_score_entry(self):
        """渲染高分输入界面"""
        title = self.font.render(self._t('high_score_entry.title'), True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(
            f"{self._t('high_score_entry.score')}: {int(self.score)}", True, COLORS['WHITE']
        )
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(score_text, score_rect)
        
        prompt_text = self.small_font.render(self._t('high_score_entry.prompt'), True, COLORS['WHITE'])
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(prompt_text, prompt_rect)
        
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 330, 300, 40)
        pygame.draw.rect(self.screen, COLORS['WHITE'], input_rect, 2)
        
        name_text = self.small_font.render(self.player_name + "_", True, COLORS['WHITE'])
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(name_text, name_rect)
        
        hint_text = self.tiny_font.render(self._t('high_score_entry.hint'), True, COLORS['LIGHT_GRAY'])
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(hint_text, hint_rect)
    
    def _render_settings(self):
        """渲染设置菜单"""
        title = self.font.render(self._t('settings.title'), True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        for i, item in enumerate(self.settings_menu_entries):
            color = COLORS['YELLOW'] if i == self.settings_menu_index else COLORS['WHITE']
            text = self.small_font.render(item['label'], True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 40))
            self.screen.blit(text, text_rect)
        
        controls = [
            self._t('settings.hint.up_down'),
            self._t('settings.hint.left_right'),
            self._t('settings.hint.enter'),
            self._t('settings.hint.esc')
        ]
        for i, control in enumerate(controls):
            text = self.tiny_font.render(control, True, COLORS['LIGHT_GRAY'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 400 + i * 20))
            self.screen.blit(text, text_rect)
            
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
