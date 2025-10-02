"""
バリデーション機能
"""
import re
from typing import Any, List, Optional, Tuple
from datetime import datetime, date

class ValidationError(Exception):
    """バリデーションエラー"""
    pass

class Validators:
    """バリデーションクラス"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """必須項目のバリデーション"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name}は必須項目です")
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, max_length: int, min_length: int = 0) -> None:
        """文字列長のバリデーション"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}は文字列である必要があります")
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name}は{min_length}文字以上である必要があります")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name}は{max_length}文字以下である必要があります")
    
    @staticmethod
    def validate_integer_range(value: int, field_name: str, min_value: int = None, max_value: int = None) -> None:
        """整数範囲のバリデーション"""
        if not isinstance(value, int):
            raise ValidationError(f"{field_name}は整数である必要があります")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name}は{min_value}以上である必要があります")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name}は{max_value}以下である必要があります")
    
    @staticmethod
    def validate_float_range(value: float, field_name: str, min_value: float = None, max_value: float = None) -> None:
        """浮動小数点範囲のバリデーション"""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name}は数値である必要があります")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name}は{min_value}以上である必要があります")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name}は{max_value}以下である必要があります")
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date, field_name: str = "日付範囲") -> None:
        """日付範囲のバリデーション"""
        if start_date > end_date:
            raise ValidationError(f"{field_name}の開始日は終了日より前である必要があります")
    
    @staticmethod
    def validate_email(email: str) -> None:
        """メールアドレスのバリデーション"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("有効なメールアドレスを入力してください")
    
    @staticmethod
    def validate_phone_number(phone: str) -> None:
        """電話番号のバリデーション"""
        # 日本の電話番号パターン
        pattern = r'^(\d{2,4}-\d{2,4}-\d{4}|\d{10,11})$'
        if not re.match(pattern, phone):
            raise ValidationError("有効な電話番号を入力してください（例: 03-1234-5678）")
    
    @staticmethod
    def validate_product_id(product_id: str) -> None:
        """商品IDのバリデーション"""
        Validators.validate_required(product_id, "商品ID")
        Validators.validate_string_length(product_id, "商品ID", 50, 1)
        
        # 商品IDの形式チェック（英数字とハイフンのみ）
        pattern = r'^[a-zA-Z0-9\-_]+$'
        if not re.match(pattern, product_id):
            raise ValidationError("商品IDは英数字、ハイフン、アンダースコアのみ使用できます")
    
    @staticmethod
    def validate_color_name(color_name: str) -> None:
        """カラー名のバリデーション"""
        Validators.validate_required(color_name, "カラー名")
        Validators.validate_string_length(color_name, "カラー名", 100, 1)
    
    @staticmethod
    def validate_size_name(size_name: str) -> None:
        """サイズ名のバリデーション"""
        Validators.validate_required(size_name, "サイズ名")
        Validators.validate_string_length(size_name, "サイズ名", 100, 1)
    
    @staticmethod
    def validate_confidence(confidence: float) -> None:
        """信頼度のバリデーション"""
        Validators.validate_float_range(confidence, "信頼度", 0.0, 1.0)
    
    @staticmethod
    def validate_database_config(config: dict, db_type: str) -> List[str]:
        """データベース設定のバリデーション"""
        errors = []
        
        if db_type == 'sqlserver':
            required_fields = ['driver', 'server', 'database']
            for field in required_fields:
                if field not in config or not config[field]:
                    errors.append(f"SQL Server設定の{field}が不足しています")
        
        elif db_type == 'mariadb':
            required_fields = ['host', 'port', 'user', 'password', 'database']
            for field in required_fields:
                if field not in config or not config[field]:
                    errors.append(f"MariaDB設定の{field}が不足しています")
            
            # ポート番号のチェック
            if 'port' in config:
                try:
                    port = int(config['port'])
                    if port < 1 or port > 65535:
                        errors.append("ポート番号は1-65535の範囲である必要があります")
                except ValueError:
                    errors.append("ポート番号は数値である必要があります")
        
        return errors
    
    @staticmethod
    def validate_conversion_rule(rule_data: dict) -> List[str]:
        """変換ルールのバリデーション"""
        errors = []
        
        # 必須項目のチェック
        required_fields = ['source_name', 'target_id', 'target_name']
        for field in required_fields:
            if field not in rule_data or not rule_data[field]:
                errors.append(f"変換ルールの{field}が不足しています")
        
        # 信頼度のチェック
        if 'confidence' in rule_data:
            try:
                confidence = float(rule_data['confidence'])
                if confidence < 0.0 or confidence > 1.0:
                    errors.append("信頼度は0.0-1.0の範囲である必要があります")
            except (ValueError, TypeError):
                errors.append("信頼度は数値である必要があります")
        
        return errors
