# -*- coding: utf-8 -*-
import yaml


class SettingService:
    def __init__(self):
        self.settings = self.load_config()

    @staticmethod
    def load_config():
        with open('config.yaml') as f:
            config = yaml.full_load(f)
            return config

    def save_config(self, cfg):
        self.settings['color_range']['low'] = cfg['low_color']
        self.settings['color_range']['high'] = cfg['high_color']
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(self.settings, f)
