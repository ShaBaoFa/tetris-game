import json
import os
from datetime import datetime
from typing import Dict, Any
import pygame

class SettingsManager:
    """设置管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化设置管理器"""
        self.data_dir = data_dir
        self.settings_file = os.path.join(data_dir, "settings.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 默认设置
        self.default_settings = {
            'difficulty': 'MEDIUM',
            'sound_enabled': True,
            'music_enabled': True,
            'sound_volume': 0.7,
            'music_volume': 0.5,
            'show_ghost_piece': True,
            'show_next_piece': True,
            'show_grid': False,
            'theme': 'CLASSIC',
            'language': 'zh',
            'controls': {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'rotate': pygame.K_UP,
                'soft_drop': pygame.K_DOWN,
                'hard_drop': pygame.K_SPACE,
                'pause': pygame.K_p
            }
        }
        
        # 加载设置
        self.settings = self.default_settings.copy()
        self.load_settings()
    
    def load_settings(self) -> None:
        """加载设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 合并设置，保留新版本的字段
                    self.settings.update(loaded_settings)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载设置失败: {e}")
    
    def save_settings(self) -> bool:
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"保存设置失败: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """设置值"""
        if key in self.settings:
            self.settings[key] = value
            return self.save_settings()
        return False
    
    def get_control(self, action: str) -> int:
        """获取控制键"""
        return self.settings.get('controls', {}).get(action, 0)
    
    def set_control(self, action: str, key_code: int) -> bool:
        """设置控制键"""
        if 'controls' not in self.settings:
            self.settings['controls'] = {}
        self.settings['controls'][action] = key_code
        return self.save_settings()
    
    def reset_to_default(self) -> bool:
        """重置为默认设置"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def export_settings(self, filename: str) -> bool:
        """导出设置"""
        try:
            data = {
                'export_date': datetime.now().isoformat(),
                'settings': self.settings
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"导出设置失败: {e}")
            return False
