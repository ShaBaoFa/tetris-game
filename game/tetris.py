import random
from .constants import SHAPES, PIECE_COLORS, GRID_WIDTH, GRID_HEIGHT

class Tetromino:
    """俄罗斯方块类"""
    
    def __init__(self, shape_index=None):
        """初始化俄罗斯方块"""
        if shape_index is None:
            shape_index = random.randint(0, len(SHAPES) - 1)
        
        self.shape_index = shape_index
        self.shape = [row[:] for row in SHAPES[shape_index]]
        self.color = PIECE_COLORS[shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        
    def rotate(self):
        """旋转方块"""
        # 顺时针旋转90度
        rotated = list(zip(*self.shape[::-1]))
        return [list(row) for row in rotated]
    
    def get_shape_positions(self):
        """获取方块占据的所有位置"""
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x, self.y + y))
        return positions
    
    def copy(self):
        """创建方块副本"""
        new_piece = Tetromino(self.shape_index)
        new_piece.shape = [row[:] for row in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        return new_piece

class GameBoard:
    """游戏板类"""
    
    def __init__(self):
        """初始化游戏板"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.ghost_piece = None
        
    def create_new_piece(self):
        """创建新方块"""
        self.current_piece = self.next_piece if self.next_piece else Tetromino()
        self.next_piece = Tetromino()
        self.update_ghost_piece()
        
        # 检查游戏是否结束
        if not self._is_valid_position(self.current_piece, 0, 0):
            return False
        return True
    
    def _is_valid_position(self, piece, dx=0, dy=0, test_shape=None):
        """检查方块位置是否有效"""
        shape = test_shape if test_shape else piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    # 检查边界
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    
                    # 检查碰撞
                    if new_y >= 0 and self.grid[new_y][new_x] != 0:
                        return False
        return True
    
    def move_piece(self, dx, dy):
        """移动方块"""
        if self.current_piece and self._is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            self.update_ghost_piece()
            return True
        return False
    
    def rotate_piece(self):
        """旋转方块"""
        if not self.current_piece:
            return False
            
        # 尝试旋转
        rotated_shape = self.current_piece.rotate()
        
        # 检查旋转后的位置是否有效
        if self._is_valid_position(self.current_piece, 0, 0, rotated_shape):
            self.current_piece.shape = rotated_shape
            self.update_ghost_piece()
            return True
            
        # 尝试墙踢（Wall Kick）
        for kick_x, kick_y in [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]:
            if self._is_valid_position(self.current_piece, kick_x, kick_y, rotated_shape):
                self.current_piece.x += kick_x
                self.current_piece.y += kick_y
                self.current_piece.shape = rotated_shape
                self.update_ghost_piece()
                return True
                
        return False
    
    def update_ghost_piece(self):
        """更新幽灵方块（显示方块落点）"""
        if not self.current_piece:
            self.ghost_piece = None
            return
            
        ghost = self.current_piece.copy()
        while self._is_valid_position(ghost, 0, 1):
            ghost.y += 1
        self.ghost_piece = ghost
    
    def lock_piece(self):
        """锁定方块到游戏板"""
        if not self.current_piece:
            return 0
            
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + y
                    grid_x = self.current_piece.x + x
                    if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                        self.grid[grid_y][grid_x] = self.current_piece.shape_index + 1  # 1-7表示不同颜色的方块
        
        lines_cleared = self.clear_lines()
        self.current_piece = None
        self.ghost_piece = None
        return lines_cleared
    
    def clear_lines(self):
        """清除完整的行"""
        lines_to_clear = []
        
        # 找出需要清除的行
        for y in range(GRID_HEIGHT):
            if all(cell != 0 for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        # 清除行并下移
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        return len(lines_to_clear)
    
    def get_game_state(self):
        """获取游戏板状态（用于AI）"""
        state = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # 复制已锁定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    state[y][x] = 1
        
        # 添加当前方块
        if self.current_piece:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        grid_y = self.current_piece.y + y
                        grid_x = self.current_piece.x + x
                        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                            state[grid_y][grid_x] = 1
        
        return state
    
    def reset(self):
        """重置游戏板"""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.ghost_piece = None