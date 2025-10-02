"""
データベース接続設定
"""
from typing import Dict, Any
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class DatabaseConfig:
    """データベース接続設定クラス"""
    
    def __init__(self):
        """初期化"""
        self.sqlserver_config = {
            'driver': os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 17 for SQL Server'),
            'server': os.getenv('SQLSERVER_SERVER', 'localhost'),
            'database': os.getenv('SQLSERVER_DATABASE', 'your_database'),
            'trusted_connection': os.getenv('SQLSERVER_TRUSTED_CONNECTION', 'yes'),
            'uid': os.getenv('SQLSERVER_UID', ''),
            'pwd': os.getenv('SQLSERVER_PWD', '')
        }
        
        self.mariadb_config = {
            'host': os.getenv('MARIADB_HOST', 'localhost'),
            'port': int(os.getenv('MARIADB_PORT', '3306')),
            'user': os.getenv('MARIADB_USER', 'your_user'),
            'password': os.getenv('MARIADB_PASSWORD', 'your_password'),
            'database': os.getenv('MARIADB_DATABASE', 'your_database'),
            'charset': 'utf8mb4'
        }
        
        self.sqlite_config = {
            'database': os.getenv('SQLITE_DATABASE', 'data/conversion.db')
        }
    
    def get_sqlserver_connection_string(self) -> str:
        """SQL Server接続文字列を取得"""
        config = self.sqlserver_config
        
        if config['trusted_connection'] == 'yes':
            return (
                f"DRIVER={{{config['driver']}}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{config['driver']}}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"UID={config['uid']};"
                f"PWD={config['pwd']};"
            )
    
    def get_mariadb_connection_string(self) -> str:
        """MariaDB接続文字列を取得"""
        config = self.mariadb_config
        return (
            f"mysql+pymysql://{config['user']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['database']}"
            f"?charset={config['charset']}"
        )
    
    def get_sqlite_connection_string(self) -> str:
        """SQLite接続文字列を取得"""
        config = self.sqlite_config
        return f"sqlite:///{config['database']}"
