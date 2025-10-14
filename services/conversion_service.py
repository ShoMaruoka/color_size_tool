"""
変換処理サービス
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from sqlalchemy import text

from .database_service import DatabaseService
from ..models.conversion import ConversionRule, ConversionHistory, ConversionBatch
from ..config.logging_config import app_logger
from ..utils.error_handlers import DatabaseError, ConversionError, ValidationError

class ConversionService:
    """変換処理サービスクラス"""
    
    def __init__(self, db_service: Optional[DatabaseService] = None):
        """初期化"""
        self.db_service = db_service or DatabaseService()
        self._ensure_conversion_tables()
    
    def _ensure_conversion_tables(self) -> None:
        """変換テーブルの存在確認と作成"""
        try:
            # テーブルが存在しない場合は作成
            self.db_service.create_tables('sqlite')
            app_logger.info("変換テーブルの確認が完了しました")
        except Exception as e:
            app_logger.error(f"変換テーブルの確認に失敗しました: {e}")
            raise DatabaseError(f"変換テーブルの確認に失敗しました: {str(e)}")
    
    # 変換ルール管理
    def get_color_rules(self) -> List[ConversionRule]:
        """カラー変換ルールを取得"""
        try:
            query = """
            SELECT id, source_color_name, target_color_id, target_color_name, 
                   confidence, is_active, created_at, updated_at
            FROM color_conversion_rules
            WHERE is_active = 1
            ORDER BY source_color_name
            """
            
            df = self.db_service.execute_query(query, 'sqlite')
            
            rules = []
            for _, row in df.iterrows():
                rule = ConversionRule(
                    id=row['id'],
                    source_name=row['source_color_name'],
                    target_id=row['target_color_id'],
                    target_name=row['target_color_name'],
                    confidence=row['confidence'],
                    is_active=bool(row['is_active']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                rules.append(rule)
            
            app_logger.info(f"カラー変換ルールを取得しました: {len(rules)}件")
            return rules
            
        except Exception as e:
            app_logger.error(f"カラー変換ルール取得エラー: {e}")
            raise DatabaseError(f"カラー変換ルールの取得に失敗しました: {str(e)}")
    
    def get_size_rules(self) -> List[ConversionRule]:
        """サイズ変換ルールを取得"""
        try:
            query = """
            SELECT id, source_size_name, target_size_id, target_size_name, 
                   confidence, is_active, created_at, updated_at
            FROM size_conversion_rules
            WHERE is_active = 1
            ORDER BY source_size_name
            """
            
            df = self.db_service.execute_query(query, 'sqlite')
            
            rules = []
            for _, row in df.iterrows():
                rule = ConversionRule(
                    id=row['id'],
                    source_name=row['source_size_name'],
                    target_id=row['target_size_id'],
                    target_name=row['target_size_name'],
                    confidence=row['confidence'],
                    is_active=bool(row['is_active']),
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                rules.append(rule)
            
            app_logger.info(f"サイズ変換ルールを取得しました: {len(rules)}件")
            return rules
            
        except Exception as e:
            app_logger.error(f"サイズ変換ルール取得エラー: {e}")
            raise DatabaseError(f"サイズ変換ルールの取得に失敗しました: {str(e)}")
    
    def add_color_rule(
        self, 
        source_name: str, 
        target_id: int, 
        target_name: str, 
        confidence: float = 1.0
    ) -> int:
        """カラー変換ルールを追加"""
        try:
            query = """
            INSERT INTO color_conversion_rules 
            (source_color_name, target_color_id, target_color_name, confidence, is_active, created_at, updated_at)
            VALUES (:source_name, :target_id, :target_name, :confidence, 1, :now, :now)
            """
            
            now = datetime.now()
            params = {
                'source_name': source_name,
                'target_id': target_id,
                'target_name': target_name,
                'confidence': confidence,
                'now': now
            }
            
            self.db_service.execute_non_query(query, 'sqlite', params)
            app_logger.info(f"カラー変換ルールを追加しました: {source_name} -> {target_name}")
            
            # 追加されたIDを取得
            id_query = "SELECT last_insert_rowid() as id"
            result = self.db_service.execute_query(id_query, 'sqlite')
            return result.iloc[0]['id']
            
        except Exception as e:
            app_logger.error(f"カラー変換ルール追加エラー: {e}")
            raise DatabaseError(f"カラー変換ルールの追加に失敗しました: {str(e)}")
    
    def add_size_rule(
        self, 
        source_name: str, 
        target_id: int, 
        target_name: str, 
        confidence: float = 1.0
    ) -> int:
        """サイズ変換ルールを追加"""
        try:
            query = """
            INSERT INTO size_conversion_rules 
            (source_size_name, target_size_id, target_size_name, confidence, is_active, created_at, updated_at)
            VALUES (:source_name, :target_id, :target_name, :confidence, 1, :now, :now)
            """
            
            now = datetime.now()
            params = {
                'source_name': source_name,
                'target_id': target_id,
                'target_name': target_name,
                'confidence': confidence,
                'now': now
            }
            
            self.db_service.execute_non_query(query, 'sqlite', params)
            app_logger.info(f"サイズ変換ルールを追加しました: {source_name} -> {target_name}")
            
            # 追加されたIDを取得
            id_query = "SELECT last_insert_rowid() as id"
            result = self.db_service.execute_query(id_query, 'sqlite')
            return result.iloc[0]['id']
            
        except Exception as e:
            app_logger.error(f"サイズ変換ルール追加エラー: {e}")
            raise DatabaseError(f"サイズ変換ルールの追加に失敗しました: {str(e)}")
    
    def update_rule(self, rule_id: int, rule_type: str, **kwargs) -> None:
        """変換ルールを更新"""
        try:
            table_name = f"{rule_type}_conversion_rules"
            update_fields = []
            params = {'rule_id': rule_id, 'now': datetime.now()}
            
            for key, value in kwargs.items():
                if key in ['target_id', 'target_name', 'confidence', 'is_active']:
                    update_fields.append(f"{key} = :{key}")
                    params[key] = value
            
            if not update_fields:
                raise ValidationError("更新するフィールドが指定されていません")
            
            update_fields.append("updated_at = :now")
            query = f"UPDATE {table_name} SET {', '.join(update_fields)} WHERE id = :rule_id"
            
            self.db_service.execute_non_query(query, 'sqlite', params)
            app_logger.info(f"{rule_type}変換ルールを更新しました: ID {rule_id}")
            
        except Exception as e:
            app_logger.error(f"変換ルール更新エラー: {e}")
            raise DatabaseError(f"変換ルールの更新に失敗しました: {str(e)}")
    
    def delete_rule(self, rule_id: int, rule_type: str) -> None:
        """変換ルールを削除（論理削除）"""
        try:
            table_name = f"{rule_type}_conversion_rules"
            query = f"UPDATE {table_name} SET is_active = 0, updated_at = :now WHERE id = :rule_id"
            
            params = {'rule_id': rule_id, 'now': datetime.now()}
            self.db_service.execute_non_query(query, 'sqlite', params)
            app_logger.info(f"{rule_type}変換ルールを削除しました: ID {rule_id}")
            
        except Exception as e:
            app_logger.error(f"変換ルール削除エラー: {e}")
            raise DatabaseError(f"変換ルールの削除に失敗しました: {str(e)}")
    
    # 自動変換機能
    def convert_color(self, color_name: str) -> Optional[Tuple[int, str, float]]:
        """カラー名をIDに変換"""
        try:
            if not color_name:
                return None
            
            # 完全一致を優先
            rules = self.get_color_rules()
            for rule in rules:
                if rule.source_name.lower() == color_name.lower():
                    return (rule.target_id, rule.target_name, rule.confidence)
            
            # 部分一致を試行
            for rule in rules:
                if color_name.lower() in rule.source_name.lower() or rule.source_name.lower() in color_name.lower():
                    return (rule.target_id, rule.target_name, rule.confidence * 0.8)  # 信頼度を下げる
            
            app_logger.warning(f"カラー変換ルールが見つかりません: {color_name}")
            return None
            
        except Exception as e:
            app_logger.error(f"カラー変換エラー: {e}")
            raise ConversionError(f"カラー変換に失敗しました: {str(e)}")
    
    def convert_size(self, size_name: str) -> Optional[Tuple[int, str, float]]:
        """サイズ名をIDに変換"""
        try:
            if not size_name:
                return None
            
            # 完全一致を優先
            rules = self.get_size_rules()
            for rule in rules:
                if rule.source_name.lower() == size_name.lower():
                    return (rule.target_id, rule.target_name, rule.confidence)
            
            # 部分一致を試行
            for rule in rules:
                if size_name.lower() in rule.source_name.lower() or rule.source_name.lower() in size_name.lower():
                    return (rule.target_id, rule.target_name, rule.confidence * 0.8)  # 信頼度を下げる
            
            app_logger.warning(f"サイズ変換ルールが見つかりません: {size_name}")
            return None
            
        except Exception as e:
            app_logger.error(f"サイズ変換エラー: {e}")
            raise ConversionError(f"サイズ変換に失敗しました: {str(e)}")
    
    def convert_composite(self, composite_value: str) -> Tuple[Optional[int], Optional[int], float]:
        """複合値をカラーIDとサイズIDに変換"""
        try:
            if not composite_value:
                return (None, None, 0.0)
            
            # 複合値からカラー名とサイズ名を抽出
            color_name, size_name = self._parse_composite_value(composite_value)
            
            color_result = self.convert_color(color_name) if color_name else None
            size_result = self.convert_size(size_name) if size_name else None
            
            color_id = color_result[0] if color_result else None
            size_id = size_result[0] if size_result else None
            
            # 信頼度を計算
            confidence = 0.0
            if color_result and size_result:
                confidence = (color_result[2] + size_result[2]) / 2
            elif color_result:
                confidence = color_result[2] * 0.5
            elif size_result:
                confidence = size_result[2] * 0.5
            
            return (color_id, size_id, confidence)
            
        except Exception as e:
            app_logger.error(f"複合値変換エラー: {e}")
            raise ConversionError(f"複合値変換に失敗しました: {str(e)}")
    
    def _parse_composite_value(self, composite_value: str) -> Tuple[Optional[str], Optional[str]]:
        """複合値からカラー名とサイズ名を抽出"""
        try:
            # 一般的な区切り文字で分割
            separators = ['/', '-', '_', ' ']
            
            for sep in separators:
                if sep in composite_value:
                    parts = composite_value.split(sep, 1)
                    if len(parts) == 2:
                        return (parts[0].strip(), parts[1].strip())
            
            # 区切り文字がない場合は、カラー名のみと仮定
            return (composite_value.strip(), None)
            
        except Exception as e:
            app_logger.error(f"複合値解析エラー: {e}")
            return (None, None)
    
    # 変換履歴管理
    def add_conversion_history(
        self, 
        product_id: str, 
        original_value: str, 
        converted_color_id: Optional[int], 
        converted_size_id: Optional[int], 
        conversion_type: str, 
        status: str, 
        confidence: float = 1.0, 
        error_message: Optional[str] = None
    ) -> int:
        """変換履歴を追加"""
        try:
            query = """
            INSERT INTO conversion_history 
            (product_id, original_value, converted_color_id, converted_size_id, 
             conversion_type, status, confidence, error_message, created_at, updated_at)
            VALUES (:product_id, :original_value, :converted_color_id, :converted_size_id, 
                    :conversion_type, :status, :confidence, :error_message, :now, :now)
            """
            
            now = datetime.now()
            params = {
                'product_id': product_id,
                'original_value': original_value,
                'converted_color_id': converted_color_id,
                'converted_size_id': converted_size_id,
                'conversion_type': conversion_type,
                'status': status,
                'confidence': confidence,
                'error_message': error_message,
                'now': now
            }
            
            self.db_service.execute_non_query(query, 'sqlite', params)
            
            # 追加されたIDを取得
            id_query = "SELECT last_insert_rowid() as id"
            result = self.db_service.execute_query(id_query, 'sqlite')
            history_id = result.iloc[0]['id']
            
            app_logger.info(f"変換履歴を追加しました: ID {history_id}")
            return history_id
            
        except Exception as e:
            app_logger.error(f"変換履歴追加エラー: {e}")
            raise DatabaseError(f"変換履歴の追加に失敗しました: {str(e)}")
    
    def get_conversion_history(self, limit: int = 100) -> List[ConversionHistory]:
        """変換履歴を取得"""
        try:
            query = """
            SELECT id, product_id, original_value, converted_color_id, converted_size_id,
                   conversion_type, status, confidence, error_message, created_at, updated_at
            FROM conversion_history
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            df = self.db_service.execute_query(query, 'sqlite', {'limit': limit})
            
            histories = []
            for _, row in df.iterrows():
                history = ConversionHistory(
                    id=row['id'],
                    product_id=row['product_id'],
                    original_value=row['original_value'],
                    converted_color_id=row['converted_color_id'],
                    converted_size_id=row['converted_size_id'],
                    conversion_type=row['conversion_type'],
                    status=row['status'],
                    confidence=row['confidence'],
                    error_message=row['error_message'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                histories.append(history)
            
            app_logger.info(f"変換履歴を取得しました: {len(histories)}件")
            return histories
            
        except Exception as e:
            app_logger.error(f"変換履歴取得エラー: {e}")
            raise DatabaseError(f"変換履歴の取得に失敗しました: {str(e)}")
    
    # 初期データの投入
    def initialize_sample_rules(self) -> None:
        """サンプル変換ルールを初期化"""
        try:
            # カラー変換ルール
            color_rules = [
                ('レッド', 1, 'Red', 1.0),
                ('ブルー', 2, 'Blue', 1.0),
                ('グリーン', 3, 'Green', 1.0),
                ('イエロー', 4, 'Yellow', 1.0),
                ('ブラック', 5, 'Black', 1.0),
                ('ホワイト', 6, 'White', 1.0),
                ('ピンク', 7, 'Pink', 1.0),
                ('オレンジ', 8, 'Orange', 1.0),
            ]
            
            for source_name, target_id, target_name, confidence in color_rules:
                try:
                    self.add_color_rule(source_name, target_id, target_name, confidence)
                except Exception as e:
                    app_logger.warning(f"カラールール追加をスキップ: {source_name} - {e}")
            
            # サイズ変換ルール
            size_rules = [
                ('S', 1, 'Small', 1.0),
                ('M', 2, 'Medium', 1.0),
                ('L', 3, 'Large', 1.0),
                ('XL', 4, 'Extra Large', 1.0),
                ('XXL', 5, 'Double Extra Large', 1.0),
                ('XS', 6, 'Extra Small', 1.0),
            ]
            
            for source_name, target_id, target_name, confidence in size_rules:
                try:
                    self.add_size_rule(source_name, target_id, target_name, confidence)
                except Exception as e:
                    app_logger.warning(f"サイズルール追加をスキップ: {source_name} - {e}")
            
            app_logger.info("サンプル変換ルールの初期化が完了しました")
            
        except Exception as e:
            app_logger.error(f"サンプルルール初期化エラー: {e}")
            raise DatabaseError(f"サンプルルールの初期化に失敗しました: {str(e)}")
