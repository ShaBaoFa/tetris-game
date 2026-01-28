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

class GameEngine:
    """游戏引擎类"""
    
    def __init__(self):
        """初始化游戏引擎"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 - Advanced Tetris")
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
        self.menu_items = ['开始游戏', '高分榜', '统计数据', '设置', '退出']
        
        # 设置菜单状态
        self.settings_menu_index = 0
        self.settings_menu_items = [
            '难度: {0}'.format(self.difficulty),
            '音效: {0}'.format('开启' if self.settings_manager.get_setting('sound_enabled') else '关闭'),
            '音乐: {0}'.format('开启' if self.settings_manager.get_setting('music_enabled') else '关闭'),
            '幽灵方块: {0}'.format('开启' if self.settings_manager.get_setting('show_ghost_piece') else '关闭'),
            '主题: {0}'.format(self.settings_manager.get_setting('theme', 'CLASSIC')),
            '重置设置',
            '返回'
        ]
        
        # 输入状态
        self.entering_name = False
        self.player_name = ""
        
        # 初始化游戏
        self.board.create_new_piece()
        
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
                self.player_name, int(self.score), self.level, self.lines_cleared
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
                    self.player_name, int(self.score), self.level, self.lines_cleared
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
        item = self.menu_items[self.menu_index]
        
        if item == '开始游戏':
            self.start_new_game()
        elif item == '高分榜':
            self.game_state = 'HIGH_SCORES'
        elif item == '统计数据':
            self.game_state = 'STATISTICS'
        elif item == '设置':
            self.game_state = 'SETTINGS'
            self._update_settings_menu()
        elif item == '退出':
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
            self.settings_menu_index = (self.settings_menu_index - 1) % len(self.settings_menu_items)
        elif key == pygame.K_DOWN:
            self.settings_menu_index = (self.settings_menu_index + 1) % len(self.settings_menu_items)
        elif key == pygame.K_RETURN:
            self._execute_settings_item()
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._adjust_setting(key)
        elif key == pygame.K_ESCAPE:
            self.game_state = 'MENU'
    
    def _execute_settings_item(self):
        """执行设置项"""
        item = self.settings_menu_items[self.settings_menu_index]
        
        if item.startswith('难度:'):
            difficulties = ['EASY', 'MEDIUM', 'HARD', 'EXPERT']
            current_index = difficulties.index(self.difficulty)
            next_index = (current_index + 1) % len(difficulties)
            self.difficulty = difficulties[next_index]
            self.settings_manager.set_setting('difficulty', self.difficulty)
            self._update_settings_menu()
        elif item.startswith('音效:'):
            current = self.settings_manager.get_setting('sound_enabled', True)
            self.settings_manager.set_setting('sound_enabled', not current)
            self._update_settings_menu()
        elif item.startswith('音乐:'):
            current = self.settings_manager.get_setting('music_enabled', True)
            self.settings_manager.set_setting('music_enabled', not current)
            self._update_settings_menu()
        elif item.startswith('幽灵方块:'):
            current = self.settings_manager.get_setting('show_ghost_piece', True)
            self.settings_manager.set_setting('show_ghost_piece', not current)
            self._update_settings_menu()
        elif item.startswith('主题:'):
            themes = list(THEMES.keys())
            current = self.settings_manager.get_setting('theme', 'CLASSIC')
            current_index = themes.index(current) if current in themes else 0
            next_index = (current_index + 1) % len(themes)
            self.settings_manager.set_setting('theme', themes[next_index])
            self.theme = THEMES.get(themes[next_index], THEMES['CLASSIC'])
            self._update_settings_menu()
        elif item == '重置设置':
            self.settings_manager.reset_to_default()
            self.difficulty = self.settings_manager.get_setting('difficulty', 'MEDIUM')
            self.theme = THEMES.get(self.settings_manager.get_setting('theme', 'CLASSIC'), THEMES['CLASSIC'])
            self._update_settings_menu()
        elif item == '返回':
            self.game_state = 'MENU'
        
        self.sound_manager.update_settings()
        if self.settings_manager.get_setting('music_enabled', True):
            self.sound_manager.play_music()
        else:
            self.sound_manager.stop_music()
    
    def _adjust_setting(self, key):
        """调整设置值（左右键）"""
        item = self.settings_menu_items[self.settings_menu_index]
        if item.startswith('难度:'):
            difficulties = ['EASY', 'MEDIUM', 'HARD', 'EXPERT']
            current_index = difficulties.index(self.difficulty)
            if key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(difficulties)
            else:
                current_index = (current_index + 1) % len(difficulties)
            self.difficulty = difficulties[current_index]
            self.settings_manager.set_setting('difficulty', self.difficulty)
            self._update_settings_menu()
        elif item.startswith('主题:'):
            themes = list(THEMES.keys())
            current = self.settings_manager.get_setting('theme', 'CLASSIC')
            current_index = themes.index(current) if current in themes else 0
            if key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(themes)
            else:
                current_index = (current_index + 1) % len(themes)
            self.settings_manager.set_setting('theme', themes[current_index])
            self.theme = THEMES.get(themes[current_index], THEMES['CLASSIC'])
            self._update_settings_menu()
    
    def _update_settings_menu(self):
        """更新设置菜单显示"""
        self.settings_menu_items = [
            '难度: {0}'.format(self.difficulty),
            '音效: {0}'.format('开启' if self.settings_manager.get_setting('sound_enabled') else '关闭'),
            '音乐: {0}'.format('开启' if self.settings_manager.get_setting('music_enabled') else '关闭'),
            '幽灵方块: {0}'.format('开启' if self.settings_manager.get_setting('show_ghost_piece') else '关闭'),
            '主题: {0}'.format(self.settings_manager.get_setting('theme', 'CLASSIC')),
            '重置设置',
            '返回'
        ]
        self.settings_menu_index = min(self.settings_menu_index, len(self.settings_menu_items) - 1)
    
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
        title = self.font.render("俄罗斯方块", True, COLORS['WHITE'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        for i, item in enumerate(self.menu_items):
            color = COLORS['YELLOW'] if i == self.menu_index else COLORS['WHITE']
            text = self.small_font.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 40))
            self.screen.blit(text, text_rect)
        
        controls = [
            "使用 ↑↓ 选择菜单",
            "按 ENTER 确认",
            "按 ESC 退出游戏"
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
        
        next_text = self.small_font.render("下一个:", True, COLORS['WHITE'])
        self.screen.blit(next_text, (sidebar_x, 20))
        
        if self.board.next_piece:
            for y, row in enumerate(self.board.next_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.board.next_piece.color,
                                         (sidebar_x + x * 20, 60 + y * 20, 18, 18))
        
        score_text = self.small_font.render(f"分数: {int(self.score)}", True, COLORS['WHITE'])
        self.screen.blit(score_text, (sidebar_x, 150))
        
        level_text = self.small_font.render(f"等级: {self.level}", True, COLORS['WHITE'])
        self.screen.blit(level_text, (sidebar_x, 180))
        
        lines_text = self.small_font.render(f"行数: {self.lines_cleared}", True, COLORS['WHITE'])
        self.screen.blit(lines_text, (sidebar_x, 210))
        
        diff_text = self.small_font.render(f"难度: {self.difficulty}", True, COLORS['WHITE'])
        self.screen.blit(diff_text, (sidebar_x, 240))
        
        controls_y = 320
        controls = [
            "控制:",
            "← → 移动",
            "↑ 旋转",
            "↓ 软降",
            "空格 硬降",
            "P 暂停",
            "ESC 菜单"
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
        
        pause_text = self.font.render("游戏暂停", True, COLORS['WHITE'])
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.small_font.render("按 P 继续游戏", True, COLORS['WHITE'])
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(resume_text, resume_rect)
    
    def _render_game_over_overlay(self):
        """渲染游戏结束覆盖层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['BLACK'])
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("游戏结束", True, COLORS['RED'])
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(game_over_text, game_over_rect)
        
        final_score_text = self.small_font.render(f"最终分数: {int(self.score)}", True, COLORS['WHITE'])
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)
        
        restart_text = self.small_font.render("按 SPACE 继续", True, COLORS['WHITE'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(restart_text, restart_rect)
        
        menu_text = self.small_font.render("按 ESC 返回菜单", True, COLORS['WHITE'])
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(menu_text, menu_rect)
    
    def _render_high_scores(self):
        """渲染高分榜"""
        title = self.font.render("高分榜", True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        high_scores = self.high_score_manager.get_high_scores()
        headers = ['排名', '玩家', '分数', '等级', '行数', '日期']
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
        
        back_text = self.small_font.render("按 ESC 返回菜单", True, COLORS['WHITE'])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(back_text, back_rect)
    
    def _render_statistics(self):
        """渲染统计数据"""
        title = self.font.render("游戏统计", True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        stats = self.stats_manager.get_statistics()
        stat_items = [
            f"总游戏次数: {stats['total_games']}",
            f"总游戏时间: {stats['total_play_time_formatted']}",
            f"总清除行数: {stats['total_lines_cleared']}",
            f"总得分: {stats['total_score']}",
            f"最高分数: {stats['highest_score']}",
            f"最高等级: {stats['highest_level']}",
            f"单局最多行数: {stats['most_lines_cleared']}",
            f"平均分数: {stats['average_score']}",
            f"平均行数: {stats['average_lines']}",
            f"平均游戏时长: {stats['average_session_time']}秒"
        ]
        
        y = 120
        for i, stat in enumerate(stat_items):
            text = self.small_font.render(stat, True, COLORS['WHITE'])
            self.screen.blit(text, (200, y + i * 30))
        
        y = 420
        diff_text = self.small_font.render("游戏难度分布:", True, COLORS['LIGHT_GRAY'])
        self.screen.blit(diff_text, (200, y))
        
        difficulty_stats = stats['games_per_difficulty']
        for i, (difficulty, count) in enumerate(difficulty_stats.items()):
            y = 450 + i * 25
            text = self.tiny_font.render(f"{difficulty}: {count} 场", True, COLORS['WHITE'])
            self.screen.blit(text, (220, y))
        
        back_text = self.small_font.render("按 ESC 返回菜单", True, COLORS['WHITE'])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(back_text, back_rect)
    
    def _render_high_score_entry(self):
        """渲染高分输入界面"""
        title = self.font.render("恭喜！新高分！", True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        score_text = self.font.render(f"分数: {int(self.score)}", True, COLORS['WHITE'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(score_text, score_rect)
        
        prompt_text = self.small_font.render("请输入你的名字:", True, COLORS['WHITE'])
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(prompt_text, prompt_rect)
        
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 330, 300, 40)
        pygame.draw.rect(self.screen, COLORS['WHITE'], input_rect, 2)
        
        name_text = self.small_font.render(self.player_name + "_", True, COLORS['WHITE'])
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(name_text, name_rect)
        
        hint_text = self.tiny_font.render("按 ENTER 确认, ESC 取消", True, COLORS['LIGHT_GRAY'])
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(hint_text, hint_rect)
    
    def _render_settings(self):
        """渲染设置菜单"""
        title = self.font.render("游戏设置", True, COLORS['YELLOW'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        for i, item in enumerate(self.settings_menu_items):
            color = COLORS['YELLOW'] if i == self.settings_menu_index else COLORS['WHITE']
            text = self.small_font.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 40))
            self.screen.blit(text, text_rect)
        
        controls = [
            "使用 ↑↓ 选择设置",
            "使用 ←→ 调整设置",
            "按 ENTER 确认",
            "按 ESC 返回菜单"
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
