import json
import os
from datetime import datetime
from typing import Dict, Any

class StatisticsManager:
    """统计管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化统计管理器"""
        self.data_dir = data_dir
        self.stats_file = os.path.join(data_dir, "statistics.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化统计数据
        self.stats = {
            'total_games': 0,
            'total_play_time': 0,  # 总游戏时间（秒）
            'total_lines_cleared': 0,
            'total_score': 0,
            'highest_score': 0,
            'highest_level': 0,
            'most_lines_cleared': 0,
            'games_per_difficulty': {
                'EASY': 0,
                'MEDIUM': 0,
                'HARD': 0,
                'EXPERT': 0
            },
            'session_start_time': None,
            'last_session_date': None
        }
        
        # 加载现有统计数据
        self.load_statistics()
    
    def load_statistics(self) -> None:
        """加载统计数据"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    loaded_stats = json.load(f)
                    # 合并统计数据，保留新版本的字段
                    self.stats.update(loaded_stats)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载统计数据失败: {e}")
    
    def save_statistics(self) -> bool:
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"保存统计数据失败: {e}")
            return False
    
    def start_session(self) -> None:
        """开始游戏会话"""
        self.stats['session_start_time'] = datetime.now().timestamp()
        
        # 更新最后游戏日期
        today = datetime.now().strftime('%Y-%m-%d')
        if self.stats['last_session_date'] != today:
            self.stats['last_session_date'] = today
    
    def end_session(self, play_time: float) -> None:
        """结束游戏会话"""
        if self.stats['session_start_time']:
            session_time = play_time
            self.stats['total_play_time'] += session_time
            self.stats['session_start_time'] = None
    
    def record_game(self, score: int, level: int, lines_cleared: int, difficulty: str) -> None:
        """记录一场游戏"""
        self.stats['total_games'] += 1
        self.stats['total_score'] += score
        self.stats['total_lines_cleared'] += lines_cleared
        
        # 更新最高记录
        if score > self.stats['highest_score']:
            self.stats['highest_score'] = score
        
        if level > self.stats['highest_level']:
            self.stats['highest_level'] = level
        
        if lines_cleared > self.stats['most_lines_cleared']:
            self.stats['most_lines_cleared'] = lines_cleared
        
        # 更新难度统计
        if difficulty in self.stats['games_per_difficulty']:
            self.stats['games_per_difficulty'][difficulty] += 1
        
        # 保存统计数据
        self.save_statistics()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        stats = self.stats.copy()
        
        # 计算平均值
        if stats['total_games'] > 0:
            stats['average_score'] = round(stats['total_score'] / stats['total_games'])
            stats['average_lines'] = round(stats['total_lines_cleared'] / stats['total_games'], 1)
            stats['average_session_time'] = round(
                stats['total_play_time'] / stats['total_games'], 1
            )
        else:
            stats['average_score'] = 0
            stats['average_lines'] = 0
            stats['average_session_time'] = 0
        
        stats['total_play_time_seconds'] = stats['total_play_time']
        
        return stats
    
    
    def reset_statistics(self) -> bool:
        """重置统计数据"""
        self.stats = {
            'total_games': 0,
            'total_play_time': 0,
            'total_lines_cleared': 0,
            'total_score': 0,
            'highest_score': 0,
            'highest_level': 0,
            'most_lines_cleared': 0,
            'games_per_difficulty': {
                'EASY': 0,
                'MEDIUM': 0,
                'HARD': 0,
                'EXPERT': 0
            },
            'session_start_time': None,
            'last_session_date': None
        }
        return self.save_statistics()
    
    def export_statistics(self, filename: str) -> bool:
        """导出统计数据"""
        try:
            data = {
                'export_date': datetime.now().isoformat(),
                'statistics': self.get_statistics()
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"导出统计数据失败: {e}")
            return False
    
    def get_difficulty_preference(self) -> str:
        """获取玩家偏好的难度"""
        difficulty_stats = self.stats['games_per_difficulty']
        if not any(difficulty_stats.values()):
            return 'MEDIUM'  # 默认难度
        
        return max(difficulty_stats.keys(), key=lambda x: difficulty_stats[x])
