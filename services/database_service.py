"""
データベース操作サービス
"""
from typing import Optional, Dict, Any, List
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import pandas as pd

from ..config.database import DatabaseConfig
from ..config.logging_config import app_logger

class DatabaseService:
    """データベース操作サービスクラス"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """初期化"""
        self.config = config or DatabaseConfig()
        self.engines = {}
        self.sessions = {}
        self._setup_engines()
    
    def _setup_engines(self) -> None:
        """エンジンをセットアップ"""
        try:
            # SQL Server
            sqlserver_url = self.config.get_sqlserver_connection_string()
            self.engines['sqlserver'] = create_engine(
                f"mssql+pyodbc:///?odbc_connect={sqlserver_url}",
                echo=False,
                pool_pre_ping=True
            )
            
            # MariaDB
            mariadb_url = self.config.get_mariadb_connection_string()
            self.engines['mariadb'] = create_engine(
                mariadb_url,
                echo=False,
                pool_pre_ping=True
            )
            
            # SQLite
            sqlite_url = self.config.get_sqlite_connection_string()
            self.engines['sqlite'] = create_engine(
                sqlite_url,
                echo=False,
                pool_pre_ping=True
            )
            
            app_logger.info("データベースエンジンのセットアップが完了しました")
            
        except Exception as e:
            app_logger.error(f"データベースエンジンのセットアップに失敗しました: {e}")
            raise
    
    @contextmanager
    def get_session(self, db_type: str = 'sqlite'):
        """セッションを取得（コンテキストマネージャー）"""
        if db_type not in self.engines:
            raise ValueError(f"サポートされていないデータベースタイプ: {db_type}")
        
        Session = sessionmaker(bind=self.engines[db_type])
        session = Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            app_logger.error(f"データベース操作でエラーが発生しました: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self, db_type: str = 'sqlite') -> bool:
        """データベース接続をテスト"""
        try:
            with self.get_session(db_type) as session:
                if db_type == 'sqlite':
                    session.execute(text("SELECT 1"))
                elif db_type == 'sqlserver':
                    session.execute(text("SELECT 1"))
                elif db_type == 'mariadb':
                    session.execute(text("SELECT 1"))
                
                app_logger.info(f"{db_type}への接続テストが成功しました")
                return True
                
        except Exception as e:
            app_logger.error(f"{db_type}への接続テストが失敗しました: {e}")
            return False
    
    def execute_query(self, query: str, db_type: str = 'sqlite', params: Optional[Dict] = None) -> pd.DataFrame:
        """クエリを実行してDataFrameを返す"""
        try:
            with self.get_session(db_type) as session:
                result = session.execute(text(query), params or {})
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                app_logger.info(f"クエリが正常に実行されました: {len(df)}件のレコードを取得")
                return df
                
        except Exception as e:
            app_logger.error(f"クエリの実行に失敗しました: {e}")
            raise
    
    def execute_non_query(self, query: str, db_type: str = 'sqlite', params: Optional[Dict] = None) -> int:
        """非SELECTクエリを実行して影響行数を返す"""
        try:
            with self.get_session(db_type) as session:
                result = session.execute(text(query), params or {})
                affected_rows = result.rowcount
                app_logger.info(f"クエリが正常に実行されました: {affected_rows}行が影響を受けました")
                return affected_rows
                
        except Exception as e:
            app_logger.error(f"クエリの実行に失敗しました: {e}")
            raise
    
    def create_tables(self, db_type: str = 'sqlite') -> None:
        """テーブルを作成"""
        try:
            metadata = MetaData()
            
            # カラー変換ルールテーブル
            color_conversion_rules = Table(
                'color_conversion_rules',
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('source_color_name', String(100), nullable=False),
                Column('target_color_id', Integer, nullable=False),
                Column('target_color_name', String(100), nullable=False),
                Column('confidence', Float, default=1.0),
                Column('is_active', Boolean, default=True),
                Column('created_at', DateTime),
                Column('updated_at', DateTime)
            )
            
            # サイズ変換ルールテーブル
            size_conversion_rules = Table(
                'size_conversion_rules',
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('source_size_name', String(100), nullable=False),
                Column('target_size_id', Integer, nullable=False),
                Column('target_size_name', String(100), nullable=False),
                Column('confidence', Float, default=1.0),
                Column('is_active', Boolean, default=True),
                Column('created_at', DateTime),
                Column('updated_at', DateTime)
            )
            
            # 変換履歴テーブル
            conversion_history = Table(
                'conversion_history',
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('product_id', String(50), nullable=False),
                Column('original_value', String(200), nullable=False),
                Column('converted_color_id', Integer),
                Column('converted_size_id', Integer),
                Column('conversion_type', String(20), nullable=False),
                Column('status', String(20), nullable=False),
                Column('confidence', Float, default=1.0),
                Column('error_message', String(500)),
                Column('created_at', DateTime),
                Column('updated_at', DateTime)
            )
            
            # 変換バッチテーブル
            conversion_batch = Table(
                'conversion_batch',
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('batch_name', String(100), nullable=False),
                Column('total_records', Integer, default=0),
                Column('processed_records', Integer, default=0),
                Column('successful_records', Integer, default=0),
                Column('failed_records', Integer, default=0),
                Column('status', String(20), nullable=False),
                Column('started_at', DateTime),
                Column('completed_at', DateTime),
                Column('created_at', DateTime),
                Column('updated_at', DateTime)
            )
            
            # テーブルを作成
            metadata.create_all(self.engines[db_type])
            app_logger.info(f"{db_type}のテーブル作成が完了しました")
            
        except Exception as e:
            app_logger.error(f"テーブル作成に失敗しました: {e}")
            raise
    
    def get_table_info(self, table_name: str, db_type: str = 'sqlite') -> pd.DataFrame:
        """テーブル情報を取得"""
        try:
            if db_type == 'sqlite':
                query = f"PRAGMA table_info({table_name})"
            elif db_type == 'sqlserver':
                query = f"""
                SELECT 
                    COLUMN_NAME as name,
                    DATA_TYPE as type,
                    IS_NULLABLE as notnull,
                    COLUMN_DEFAULT as dflt_value,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as pk
                FROM INFORMATION_SCHEMA.COLUMNS c
                LEFT JOIN (
                    SELECT ku.TABLE_NAME, ku.COLUMN_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                        ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                        AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
                WHERE c.TABLE_NAME = '{table_name}'
                """
            elif db_type == 'mariadb':
                query = f"""
                SELECT 
                    COLUMN_NAME as name,
                    DATA_TYPE as type,
                    IS_NULLABLE as notnull,
                    COLUMN_DEFAULT as dflt_value,
                    CASE WHEN COLUMN_KEY = 'PRI' THEN 1 ELSE 0 END as pk
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                """
            
            return self.execute_query(query, db_type)
            
        except Exception as e:
            app_logger.error(f"テーブル情報の取得に失敗しました: {e}")
            raise
