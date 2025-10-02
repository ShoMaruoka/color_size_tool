"""
アプリケーション設定
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class AppSettings:
    """アプリケーション設定クラス"""
    
    def __init__(self):
        """初期化"""
        self.app_name = "カラーサイズメンテナンスツール"
        self.app_version = "1.0.0"
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # データ取得設定
        self.data_settings = {
            'default_date_range_days': int(os.getenv('DEFAULT_DATE_RANGE_DAYS', '30')),
            'max_records_per_page': int(os.getenv('MAX_RECORDS_PER_PAGE', '1000')),
            'batch_size': int(os.getenv('BATCH_SIZE', '100'))
        }
        
        # 変換処理設定
        self.conversion_settings = {
            'auto_convert_enabled': os.getenv('AUTO_CONVERT_ENABLED', 'True').lower() == 'true',
            'backup_before_convert': os.getenv('BACKUP_BEFORE_CONVERT', 'True').lower() == 'true',
            'validate_after_convert': os.getenv('VALIDATE_AFTER_CONVERT', 'True').lower() == 'true'
        }
        
        # UI設定
        self.ui_settings = {
            'theme': os.getenv('UI_THEME', 'light'),
            'language': os.getenv('UI_LANGUAGE', 'ja'),
            'page_size': int(os.getenv('UI_PAGE_SIZE', '20'))
        }
        
        # ログ設定
        self.log_settings = {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE', 'logs/app.log'),
            'max_log_size': int(os.getenv('MAX_LOG_SIZE', '10485760')),  # 10MB
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5'))
        }
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        settings_map = {
            'data': self.data_settings,
            'conversion': self.conversion_settings,
            'ui': self.ui_settings,
            'log': self.log_settings
        }
        
        if category in settings_map:
            return settings_map[category].get(key, default)
        return default
    
    def update_setting(self, category: str, key: str, value: Any) -> None:
        """設定値を更新"""
        settings_map = {
            'data': self.data_settings,
            'conversion': self.conversion_settings,
            'ui': self.ui_settings,
            'log': self.log_settings
        }
        
        if category in settings_map:
            settings_map[category][key] = value
