"""
ログ設定
"""
import os
import sys
from loguru import logger
from typing import Optional
from .settings import AppSettings

class LoggingConfig:
    """ログ設定クラス"""
    
    def __init__(self, settings: Optional[AppSettings] = None):
        """初期化"""
        self.settings = settings or AppSettings()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """ログ設定をセットアップ"""
        # 既存のログハンドラーをクリア
        logger.remove()
        
        # ログレベルを設定
        log_level = self.settings.get_setting('log', 'log_level', 'INFO')
        
        # コンソール出力設定
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True
        )
        
        # ファイル出力設定
        log_file = self.settings.get_setting('log', 'log_file', 'logs/app.log')
        max_size = self.settings.get_setting('log', 'max_log_size', 10485760)
        backup_count = self.settings.get_setting('log', 'backup_count', 5)
        
        # ログディレクトリを作成
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=f"{max_size} bytes",
            retention=backup_count,
            compression="zip",
            encoding="utf-8"
        )
        
        # エラーログ用の別ファイル
        error_log_file = log_file.replace('.log', '_error.log')
        logger.add(
            error_log_file,
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=f"{max_size} bytes",
            retention=backup_count,
            compression="zip",
            encoding="utf-8"
        )
    
    def get_logger(self, name: str = None):
        """ロガーを取得"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def set_level(self, level: str) -> None:
        """ログレベルを設定"""
        logger.remove()
        self._setup_logging()
        logger.info(f"ログレベルを {level} に変更しました")

# グローバルロガーインスタンス
app_logger = LoggingConfig().get_logger("color_size_tool")
