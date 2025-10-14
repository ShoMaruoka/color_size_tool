"""
データ取得サービス
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
from sqlalchemy import text

from .database_service import DatabaseService
from ..models.product import Product, ProductFilter
from ..config.logging_config import app_logger
from ..utils.error_handlers import DatabaseError, ValidationError

class DataService:
    """データ取得サービスクラス"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        """初期化"""
        self.db_service = db_service or DatabaseService()
    
    def get_products(
        self, 
        product_filter: ProductFilter, 
        db_type: str = 'sqlite'
    ) -> List[Product]:
        """商品データを取得"""
        try:
            # SQLクエリを構築
            query, params = self._build_product_query(product_filter, db_type)
            
            # クエリを実行
            df = self.db_service.execute_query(query, db_type, params)
            
            # Productオブジェクトに変換
            products = []
            for _, row in df.iterrows():
                product = Product(
                    product_id=row.get('product_id', ''),
                    product_name=row.get('product_name', ''),
                    color_name=row.get('color_name'),
                    size_name=row.get('size_name'),
                    composite_value=row.get('composite_value'),
                    color_id=row.get('color_id'),
                    size_id=row.get('size_id'),
                    created_at=row.get('created_at'),
                    updated_at=row.get('updated_at')
                )
                products.append(product)
            
            app_logger.info(f"商品データを取得しました: {len(products)}件")
            return products
            
        except Exception as e:
            app_logger.error(f"商品データ取得エラー: {e}")
            raise DatabaseError(
                f"商品データの取得に失敗しました: {str(e)}",
                error_code="PRODUCT_FETCH_ERROR",
                details={'filter': product_filter.to_dict()}
            )
    
    def _build_product_query(
        self, 
        product_filter: ProductFilter, 
        db_type: str
    ) -> tuple[str, Dict[str, Any]]:
        """商品データ取得クエリを構築"""
        
        # 基本クエリ（実際のテーブル名に応じて調整が必要）
        base_query = """
        SELECT 
            product_id,
            product_name,
            color_name,
            size_name,
            composite_value,
            color_id,
            size_id,
            created_at,
            updated_at
        FROM products
        WHERE 1=1
        """
        
        params = {}
        conditions = []
        
        # 期間フィルター
        if product_filter.start_date:
            conditions.append("created_at >= :start_date")
            params['start_date'] = product_filter.start_date
        
        if product_filter.end_date:
            conditions.append("created_at <= :end_date")
            params['end_date'] = product_filter.end_date
        
        # 商品名パターンフィルター
        if product_filter.product_name_pattern:
            if db_type == 'sqlite':
                conditions.append("product_name LIKE :product_name_pattern")
            else:
                conditions.append("product_name LIKE :product_name_pattern")
            params['product_name_pattern'] = product_filter.product_name_pattern.replace('*', '%')
        
        # カラー名パターンフィルター
        if product_filter.color_name_pattern:
            conditions.append("color_name LIKE :color_name_pattern")
            params['color_name_pattern'] = product_filter.color_name_pattern.replace('*', '%')
        
        # サイズ名パターンフィルター
        if product_filter.size_name_pattern:
            conditions.append("size_name LIKE :size_name_pattern")
            params['size_name_pattern'] = product_filter.size_name_pattern.replace('*', '%')
        
        # カラーID変換状況フィルター
        if product_filter.has_color_id is not None:
            if product_filter.has_color_id:
                conditions.append("color_id IS NOT NULL")
            else:
                conditions.append("color_id IS NULL")
        
        # サイズID変換状況フィルター
        if product_filter.has_size_id is not None:
            if product_filter.has_size_id:
                conditions.append("size_id IS NOT NULL")
            else:
                conditions.append("size_id IS NULL")
        
        # 条件を結合
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # ソート
        base_query += " ORDER BY created_at DESC"
        
        # リミット
        if product_filter.limit:
            base_query += f" LIMIT {product_filter.limit}"
            if product_filter.offset:
                base_query += f" OFFSET {product_filter.offset}"
        
        return base_query, params
    
    def get_product_statistics(
        self, 
        product_filter: ProductFilter, 
        db_type: str = 'sqlite'
    ) -> Dict[str, Any]:
        """商品データの統計情報を取得"""
        try:
            # 基本統計クエリ
            stats_query = """
            SELECT 
                COUNT(*) as total_products,
                COUNT(CASE WHEN color_id IS NOT NULL THEN 1 END) as converted_colors,
                COUNT(CASE WHEN size_id IS NOT NULL THEN 1 END) as converted_sizes,
                COUNT(CASE WHEN color_id IS NULL AND size_id IS NULL THEN 1 END) as pending_conversions
            FROM products
            WHERE 1=1
            """
            
            params = {}
            conditions = []
            
            # 期間フィルター
            if product_filter.start_date:
                conditions.append("created_at >= :start_date")
                params['start_date'] = product_filter.start_date
            
            if product_filter.end_date:
                conditions.append("created_at <= :end_date")
                params['end_date'] = product_filter.end_date
            
            # 条件を結合
            if conditions:
                stats_query += " AND " + " AND ".join(conditions)
            
            # クエリを実行
            df = self.db_service.execute_query(stats_query, db_type, params)
            
            if df.empty:
                return {
                    'total_products': 0,
                    'converted_colors': 0,
                    'converted_sizes': 0,
                    'pending_conversions': 0,
                    'conversion_rate': 0.0
                }
            
            row = df.iloc[0]
            total = row['total_products']
            converted_colors = row['converted_colors']
            converted_sizes = row['converted_sizes']
            pending = row['pending_conversions']
            
            # 変換率を計算
            conversion_rate = (converted_colors + converted_sizes) / (total * 2) if total > 0 else 0.0
            
            stats = {
                'total_products': int(total),
                'converted_colors': int(converted_colors),
                'converted_sizes': int(converted_sizes),
                'pending_conversions': int(pending),
                'conversion_rate': conversion_rate
            }
            
            app_logger.info(f"統計情報を取得しました: {stats}")
            return stats
            
        except Exception as e:
            app_logger.error(f"統計情報取得エラー: {e}")
            raise DatabaseError(
                f"統計情報の取得に失敗しました: {str(e)}",
                error_code="STATS_FETCH_ERROR",
                details={'filter': product_filter.to_dict()}
            )
    
    def get_sample_products(self) -> List[Product]:
        """サンプル商品データを取得（テスト用）"""
        sample_data = [
            {
                'product_id': 'TSH001',
                'product_name': 'Tシャツ 基本型',
                'color_name': 'レッド',
                'size_name': 'M',
                'composite_value': 'レッド/M',
                'color_id': 1,
                'size_id': 2,
                'created_at': datetime(2024, 10, 1, 10, 0, 0),
                'updated_at': datetime(2024, 10, 1, 10, 0, 0)
            },
            {
                'product_id': 'TSH002',
                'product_name': 'Tシャツ 基本型',
                'color_name': 'ブルー',
                'size_name': 'L',
                'composite_value': 'ブルー/L',
                'color_id': 2,
                'size_id': 3,
                'created_at': datetime(2024, 10, 1, 10, 5, 0),
                'updated_at': datetime(2024, 10, 1, 10, 5, 0)
            },
            {
                'product_id': 'TSH003',
                'product_name': 'Tシャツ 基本型',
                'color_name': 'グリーン',
                'size_name': 'S',
                'composite_value': 'グリーン/S',
                'color_id': None,
                'size_id': 1,
                'created_at': datetime(2024, 10, 1, 10, 10, 0),
                'updated_at': datetime(2024, 10, 1, 10, 10, 0)
            },
            {
                'product_id': 'TSH004',
                'product_name': 'Tシャツ 基本型',
                'color_name': 'イエロー',
                'size_name': 'XL',
                'composite_value': 'イエロー/XL',
                'color_id': None,
                'size_id': None,
                'created_at': datetime(2024, 10, 1, 10, 15, 0),
                'updated_at': datetime(2024, 10, 1, 10, 15, 0)
            },
            {
                'product_id': 'TSH005',
                'product_name': 'Tシャツ 基本型',
                'color_name': 'ブラック',
                'size_name': 'M',
                'composite_value': 'ブラック/M',
                'color_id': 3,
                'size_id': 2,
                'created_at': datetime(2024, 10, 1, 10, 20, 0),
                'updated_at': datetime(2024, 10, 1, 10, 20, 0)
            }
        ]
        
        products = []
        for data in sample_data:
            product = Product(
                product_id=data['product_id'],
                product_name=data['product_name'],
                color_name=data['color_name'],
                size_name=data['size_name'],
                composite_value=data['composite_value'],
                color_id=data['color_id'],
                size_id=data['size_id'],
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            products.append(product)
        
        return products
    
    def validate_connection_settings(self, db_type: str) -> Dict[str, Any]:
        """接続設定の妥当性を検証"""
        try:
            config = self.db_service.config
            
            if db_type == 'sqlserver':
                required_fields = ['server', 'database']
                config_data = config.sqlserver_config
            elif db_type == 'mariadb':
                required_fields = ['host', 'user', 'database']
                config_data = config.mariadb_config
            elif db_type == 'sqlite':
                required_fields = ['database']
                config_data = config.sqlite_config
            else:
                raise ValidationError(f"サポートされていないデータベースタイプ: {db_type}")
            
            # 必須フィールドのチェック
            missing_fields = []
            for field in required_fields:
                if not config_data.get(field) or config_data[field] == 'your_database':
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'is_valid': False,
                    'missing_fields': missing_fields,
                    'message': f"以下の設定が不足しています: {', '.join(missing_fields)}"
                }
            
            return {
                'is_valid': True,
                'message': '接続設定は有効です'
            }
            
        except Exception as e:
            app_logger.error(f"接続設定検証エラー: {e}")
            return {
                'is_valid': False,
                'message': f"設定検証中にエラーが発生しました: {str(e)}"
            }
