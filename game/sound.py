import os
import pygame


class SoundManager:
    """音频管理器"""

    def __init__(self, base_dir: str, settings_manager):
        """初始化音频管理器"""
        self.base_dir = base_dir
        self.settings_manager = settings_manager
        self.sound_enabled = self.settings_manager.get_setting('sound_enabled', True)
        self.music_enabled = self.settings_manager.get_setting('music_enabled', True)
        self.sound_volume = self.settings_manager.get_setting('sound_volume', 0.7)
        self.music_volume = self.settings_manager.get_setting('music_volume', 0.5)
        self.sounds = {}
        self.music_loaded = False

        self._init_mixer()
        self._load_sounds()
        self._load_music()

    def _init_mixer(self):
        try:
            pygame.mixer.init()
        except pygame.error:
            pass

    def _load_sounds(self):
        sound_files = {
            'move': 'move.wav',
            'rotate': 'rotate.wav',
            'drop': 'drop.wav',
            'line': 'line.wav',
            'game_over': 'game_over.wav'
        }
        sounds_dir = os.path.join(self.base_dir, 'assets', 'sounds')
        for key, filename in sound_files.items():
            path = os.path.join(sounds_dir, filename)
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.sound_volume)
                    self.sounds[key] = sound
                except pygame.error:
                    continue

    def _load_music(self):
        music_path = os.path.join(self.base_dir, 'assets', 'sounds', 'bgm.ogg')
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                self.music_loaded = True
            except pygame.error:
                self.music_loaded = False

    def play_sound(self, name: str):
        if not self.sound_enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def play_music(self):
        if self.music_enabled and self.music_loaded:
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.music_loaded:
            pygame.mixer.music.stop()

    def update_settings(self):
        self.sound_enabled = self.settings_manager.get_setting('sound_enabled', True)
        self.music_enabled = self.settings_manager.get_setting('music_enabled', True)
        self.sound_volume = self.settings_manager.get_setting('sound_volume', 0.7)
        self.music_volume = self.settings_manager.get_setting('music_volume', 0.5)

        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        if self.music_loaded:
            pygame.mixer.music.set_volume(self.music_volume)
