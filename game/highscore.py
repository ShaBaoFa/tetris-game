import json
import os
from datetime import datetime
from typing import List, Dict, Any

class HighScoreManager:
    """高分管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化高分管理器"""
        self.data_dir = data_dir
        self.high_scores_file = os.path.join(data_dir, "highscores.json")
        self.max_scores = 10  # 保存最多10个高分
        self.high_scores = []
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载现有高分
        self.load_high_scores()
    
    def load_high_scores(self) -> None:
        """加载高分数据"""
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.high_scores = data.get('high_scores', [])
            else:
                self.high_scores = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载高分数据失败: {e}")
            self.high_scores = []
    
    def save_high_scores(self) -> bool:
        """保存高分数据"""
        try:
            data = {
                'high_scores': self.high_scores,
                'last_updated': datetime.now().isoformat()
            }
            
            # 创建备份
            if os.path.exists(self.high_scores_file):
                backup_file = self.high_scores_file + ".bak"
                try:
                    import shutil
                    shutil.copy2(self.high_scores_file, backup_file)
                except:
                    pass  # 备份失败不影响主操作
            
            with open(self.high_scores_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except IOError as e:
            print(f"保存高分数据失败: {e}")
            return False
    
    def add_score(self, name: str, score: int, level: int, lines: int) -> bool:
        """添加新分数"""
        if not name.strip():
            name = "匿名玩家"
        
        new_score = {
            'name': name.strip(),
            'score': score,
            'level': level,
            'lines': lines,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': datetime.now().timestamp()
        }
        
        # 检查是否应该进入排行榜
        if len(self.high_scores) < self.max_scores or score > self.get_min_score():
            self.high_scores.append(new_score)
            self.high_scores.sort(key=lambda x: x['score'], reverse=True)
            self.high_scores = self.high_scores[:self.max_scores]
            return self.save_high_scores()
        
        return False
    
    def get_high_scores(self) -> List[Dict[str, Any]]:
        """获取高分列表"""
        return self.high_scores.copy()
    
    def get_min_score(self) -> int:
        """获取排行榜最低分数"""
        if not self.high_scores:
            return 0
        return min(score['score'] for score in self.high_scores)
    
    def get_max_score(self) -> int:
        """获取最高分数"""
        if not self.high_scores:
            return 0
        return self.high_scores[0]['score']
    
    def get_rank(self, score: int) -> int:
        """获取分数排名（如果不在排行榜返回-1）"""
        for i, high_score in enumerate(self.high_scores):
            if score >= high_score['score']:
                return i + 1
        return -1
    
    def is_high_score(self, score: int) -> bool:
        """检查是否为高分"""
        return len(self.high_scores) < self.max_scores or score > self.get_min_score()
    
    def clear_all_scores(self) -> bool:
        """清除所有高分"""
        self.high_scores = []
        return self.save_high_scores()
    
    def export_scores(self, filename: str) -> bool:
        """导出分数到文件"""
        try:
            data = {
                'export_date': datetime.now().isoformat(),
                'high_scores': self.high_scores
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"导出分数失败: {e}")
            return False
    
    def import_scores(self, filename: str) -> bool:
        """从文件导入分数"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                imported_scores = data.get('high_scores', [])
                
                # 合并分数并重新排序
                all_scores = self.high_scores + imported_scores
                # 去重（相同姓名和分数的记录）
                unique_scores = []
                seen = set()
                for score in all_scores:
                    key = (score['name'], score['score'], score['timestamp'])
                    if key not in seen:
                        seen.add(key)
                        unique_scores.append(score)
                
                unique_scores.sort(key=lambda x: x['score'], reverse=True)
                self.high_scores = unique_scores[:self.max_scores]
                
                return self.save_high_scores()
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"导入分数失败: {e}")
            return False