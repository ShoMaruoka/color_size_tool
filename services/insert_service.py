"""
データ登録サービス
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from contextlib import contextmanager

from .database_service import DatabaseService
from .data_service import DataService
from ..models.product import Product
from ..models.conversion import ConversionResult
from ..config.logging_config import app_logger
from ..utils.error_handlers import DatabaseError, ValidationError

class InsertService:
    """データ登録サービスクラス"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        """初期化"""
        self.db_service = db_service or DatabaseService()
        self.data_service = DataService()
    
    def validate_insert_data(self, products: List[Product]) -> Dict[str, Any]:
        """登録データの検証"""
        try:
            validation_result = {
                'is_valid': True,
                'total_count': len(products),
                'valid_count': 0,
                'invalid_count': 0,
                'errors': [],
                'warnings': []
            }
            
            for product in products:
                product_errors = []
                product_warnings = []
                
                # 必須フィールドのチェック
                if not product.product_id:
                    product_errors.append("商品IDが未設定")
                
                if not product.product_name:
                    product_errors.append("商品名が未設定")
                
                # 変換状況のチェック
                if product.color_id is None:
                    product_warnings.append("カラーIDが未変換")
                
                if product.size_id is None:
                    product_warnings.append("サイズIDが未変換")
                
                # データ型のチェック
                if product.color_id is not None and not isinstance(product.color_id, int):
                    product_errors.append("カラーIDの型が無効")
                
                if product.size_id is not None and not isinstance(product.size_id, int):
                    product_errors.append("サイズIDの型が無効")
                
                # 結果の集計
                if product_errors:
                    validation_result['invalid_count'] += 1
                    validation_result['errors'].extend([
                        f"{product.product_id}: {error}" for error in product_errors
                    ])
                else:
                    validation_result['valid_count'] += 1
                
                if product_warnings:
                    validation_result['warnings'].extend([
                        f"{product.product_id}: {warning}" for warning in product_warnings
                    ])
            
            # 全体の妥当性判定
            if validation_result['invalid_count'] > 0:
                validation_result['is_valid'] = False
            
            app_logger.info(f"データ検証完了: 有効{validation_result['valid_count']}件, 無効{validation_result['invalid_count']}件")
            return validation_result
            
        except Exception as e:
            app_logger.error(f"データ検証エラー: {e}")
            raise ValidationError(f"データ検証に失敗しました: {str(e)}")
    
    def insert_tm9030color(self, products: List[Product], db_type: str = 'sqlite') -> Dict[str, Any]:
        """tm9030colorテーブルに登録"""
        try:
            # カラーIDが設定されている商品のみを抽出
            color_products = [p for p in products if p.color_id is not None]
            
            if not color_products:
                return {
                    'success': True,
                    'inserted_count': 0,
                    'skipped_count': len(products),
                    'message': 'カラーIDが設定されている商品がありません'
                }
            
            # 登録用のSQLクエリを構築
            query, params = self._build_tm9030color_insert_query(color_products)
            
            # トランザクション内で実行
            with self.db_service.get_session(db_type) as session:
                result = session.execute(text(query), params)
                affected_rows = result.rowcount
                session.commit()
            
            app_logger.info(f"tm9030color登録完了: {affected_rows}件")
            
            return {
                'success': True,
                'inserted_count': affected_rows,
                'skipped_count': len(products) - len(color_products),
                'message': f'{affected_rows}件のカラーデータを登録しました'
            }
            
        except Exception as e:
            app_logger.error(f"tm9030color登録エラー: {e}")
            raise DatabaseError(f"tm9030color登録に失敗しました: {str(e)}")
    
    def insert_tm9035size(self, products: List[Product], db_type: str = 'sqlite') -> Dict[str, Any]:
        """tm9035sizeテーブルに登録"""
        try:
            # サイズIDが設定されている商品のみを抽出
            size_products = [p for p in products if p.size_id is not None]
            
            if not size_products:
                return {
                    'success': True,
                    'inserted_count': 0,
                    'skipped_count': len(products),
                    'message': 'サイズIDが設定されている商品がありません'
                }
            
            # 登録用のSQLクエリを構築
            query, params = self._build_tm9035size_insert_query(size_products)
            
            # トランザクション内で実行
            with self.db_service.get_session(db_type) as session:
                result = session.execute(text(query), params)
                affected_rows = result.rowcount
                session.commit()
            
            app_logger.info(f"tm9035size登録完了: {affected_rows}件")
            
            return {
                'success': True,
                'inserted_count': affected_rows,
                'skipped_count': len(products) - len(size_products),
                'message': f'{affected_rows}件のサイズデータを登録しました'
            }
            
        except Exception as e:
            app_logger.error(f"tm9035size登録エラー: {e}")
            raise DatabaseError(f"tm9035size登録に失敗しました: {str(e)}")
    
    def _build_tm9030color_insert_query(self, products: List[Product]) -> Tuple[str, Dict[str, Any]]:
        """tm9030color登録用クエリを構築"""
        # 実際のテーブル構造に応じて調整が必要
        query = """
        INSERT INTO tm9030color 
        (product_id, product_name, color_name, color_id, created_at, updated_at)
        VALUES 
        """
        
        values_list = []
        params = {}
        
        for i, product in enumerate(products):
            values_list.append(f"(:product_id_{i}, :product_name_{i}, :color_name_{i}, :color_id_{i}, :created_at_{i}, :updated_at_{i})")
            
            params.update({
                f'product_id_{i}': product.product_id,
                f'product_name_{i}': product.product_name,
                f'color_name_{i}': product.color_name or '',
                f'color_id_{i}': product.color_id,
                f'created_at_{i}': datetime.now(),
                f'updated_at_{i}': datetime.now()
            })
        
        query += ", ".join(values_list)
        
        # 重複回避のためのON CONFLICT句（SQLiteの場合）
        query += """
        ON CONFLICT(product_id) DO UPDATE SET
            product_name = excluded.product_name,
            color_name = excluded.color_name,
            color_id = excluded.color_id,
            updated_at = excluded.updated_at
        """
        
        return query, params
    
    def _build_tm9035size_insert_query(self, products: List[Product]) -> Tuple[str, Dict[str, Any]]:
        """tm9035size登録用クエリを構築"""
        # 実際のテーブル構造に応じて調整が必要
        query = """
        INSERT INTO tm9035size 
        (product_id, product_name, size_name, size_id, created_at, updated_at)
        VALUES 
        """
        
        values_list = []
        params = {}
        
        for i, product in enumerate(products):
            values_list.append(f"(:product_id_{i}, :product_name_{i}, :size_name_{i}, :size_id_{i}, :created_at_{i}, :updated_at_{i})")
            
            params.update({
                f'product_id_{i}': product.product_id,
                f'product_name_{i}': product.product_name,
                f'size_name_{i}': product.size_name or '',
                f'size_id_{i}': product.size_id,
                f'created_at_{i}': datetime.now(),
                f'updated_at_{i}': datetime.now()
            })
        
        query += ", ".join(values_list)
        
        # 重複回避のためのON CONFLICT句（SQLiteの場合）
        query += """
        ON CONFLICT(product_id) DO UPDATE SET
            product_name = excluded.product_name,
            size_name = excluded.size_name,
            size_id = excluded.size_id,
            updated_at = excluded.updated_at
        """
        
        return query, params
    
    def batch_insert(self, products: List[Product], db_type: str = 'sqlite', 
                    insert_colors: bool = True, insert_sizes: bool = True) -> Dict[str, Any]:
        """バッチ登録処理"""
        try:
            batch_result = {
                'success': True,
                'total_products': len(products),
                'color_result': None,
                'size_result': None,
                'started_at': datetime.now(),
                'completed_at': None,
                'errors': []
            }
            
            app_logger.info(f"バッチ登録開始: {len(products)}件の商品データ")
            
            # カラーデータ登録
            if insert_colors:
                try:
                    batch_result['color_result'] = self.insert_tm9030color(products, db_type)
                    app_logger.info(f"カラーデータ登録完了: {batch_result['color_result']['inserted_count']}件")
                except Exception as e:
                    error_msg = f"カラーデータ登録エラー: {str(e)}"
                    batch_result['errors'].append(error_msg)
                    app_logger.error(error_msg)
            
            # サイズデータ登録
            if insert_sizes:
                try:
                    batch_result['size_result'] = self.insert_tm9035size(products, db_type)
                    app_logger.info(f"サイズデータ登録完了: {batch_result['size_result']['inserted_count']}件")
                except Exception as e:
                    error_msg = f"サイズデータ登録エラー: {str(e)}"
                    batch_result['errors'].append(error_msg)
                    app_logger.error(error_msg)
            
            batch_result['completed_at'] = datetime.now()
            
            # 全体の成功判定
            if batch_result['errors']:
                batch_result['success'] = False
            
            app_logger.info(f"バッチ登録完了: 成功={batch_result['success']}")
            return batch_result
            
        except Exception as e:
            app_logger.error(f"バッチ登録エラー: {e}")
            raise DatabaseError(f"バッチ登録に失敗しました: {str(e)}")
    
    def get_insert_summary(self, products: List[Product]) -> Dict[str, Any]:
        """登録予定データのサマリーを取得"""
        try:
            color_products = [p for p in products if p.color_id is not None]
            size_products = [p for p in products if p.size_id is not None]
            
            summary = {
                'total_products': len(products),
                'color_ready': len(color_products),
                'size_ready': len(size_products),
                'color_percentage': (len(color_products) / len(products) * 100) if products else 0,
                'size_percentage': (len(size_products) / len(products) * 100) if products else 0,
                'ready_for_insert': len([p for p in products if p.color_id is not None and p.size_id is not None]),
                'needs_attention': len([p for p in products if p.color_id is None or p.size_id is None])
            }
            
            return summary
            
        except Exception as e:
            app_logger.error(f"登録サマリー取得エラー: {e}")
            raise ValidationError(f"登録サマリーの取得に失敗しました: {str(e)}")
    
    def create_sample_tables(self, db_type: str = 'sqlite') -> None:
        """サンプルテーブルを作成（テスト用）"""
        try:
            # tm9030colorテーブル
            color_table_query = """
            CREATE TABLE IF NOT EXISTS tm9030color (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id VARCHAR(50) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                color_name VARCHAR(100),
                color_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # tm9035sizeテーブル
            size_table_query = """
            CREATE TABLE IF NOT EXISTS tm9035size (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id VARCHAR(50) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                size_name VARCHAR(100),
                size_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            with self.db_service.get_session(db_type) as session:
                session.execute(text(color_table_query))
                session.execute(text(size_table_query))
                session.commit()
            
            app_logger.info("サンプルテーブルの作成が完了しました")
            
        except Exception as e:
            app_logger.error(f"サンプルテーブル作成エラー: {e}")
            raise DatabaseError(f"サンプルテーブルの作成に失敗しました: {str(e)}")
    
    def get_existing_data(self, db_type: str = 'sqlite') -> Dict[str, Any]:
        """既存データの確認"""
        try:
            existing_data = {
                'color_count': 0,
                'size_count': 0,
                'recent_colors': [],
                'recent_sizes': []
            }
            
            # カラーデータの確認
            try:
                color_query = "SELECT COUNT(*) as count FROM tm9030color"
                color_result = self.db_service.execute_query(color_query, db_type)
                existing_data['color_count'] = color_result.iloc[0]['count'] if not color_result.empty else 0
                
                # 最新のカラーデータ
                recent_color_query = """
                SELECT product_id, product_name, color_name, color_id, created_at 
                FROM tm9030color 
                ORDER BY created_at DESC 
                LIMIT 5
                """
                recent_colors = self.db_service.execute_query(recent_color_query, db_type)
                existing_data['recent_colors'] = recent_colors.to_dict('records') if not recent_colors.empty else []
                
            except Exception as e:
                app_logger.warning(f"カラーデータ確認エラー: {e}")
            
            # サイズデータの確認
            try:
                size_query = "SELECT COUNT(*) as count FROM tm9035size"
                size_result = self.db_service.execute_query(size_query, db_type)
                existing_data['size_count'] = size_result.iloc[0]['count'] if not size_result.empty else 0
                
                # 最新のサイズデータ
                recent_size_query = """
                SELECT product_id, product_name, size_name, size_id, created_at 
                FROM tm9035size 
                ORDER BY created_at DESC 
                LIMIT 5
                """
                recent_sizes = self.db_service.execute_query(recent_size_query, db_type)
                existing_data['recent_sizes'] = recent_sizes.to_dict('records') if not recent_sizes.empty else []
                
            except Exception as e:
                app_logger.warning(f"サイズデータ確認エラー: {e}")
            
            return existing_data
            
        except Exception as e:
            app_logger.error(f"既存データ確認エラー: {e}")
            raise DatabaseError(f"既存データの確認に失敗しました: {str(e)}")
