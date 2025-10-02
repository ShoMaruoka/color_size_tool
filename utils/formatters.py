"""
フォーマッター機能
"""
from typing import Any, Optional, List, Dict
from datetime import datetime, date
import re

class Formatters:
    """フォーマッタークラス"""
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """日時をフォーマット"""
        if dt is None:
            return ""
        return dt.strftime(format_str)
    
    @staticmethod
    def format_date(d: date, format_str: str = "%Y-%m-%d") -> str:
        """日付をフォーマット"""
        if d is None:
            return ""
        return d.strftime(format_str)
    
    @staticmethod
    def format_currency(amount: float, currency: str = "¥") -> str:
        """通貨をフォーマット"""
        if amount is None:
            return ""
        return f"{currency}{amount:,.0f}"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """パーセンテージをフォーマット"""
        if value is None:
            return ""
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """ファイルサイズをフォーマット"""
        if size_bytes is None:
            return ""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """電話番号をフォーマット"""
        if not phone:
            return ""
        
        # 数字のみ抽出
        digits = re.sub(r'\D', '', phone)
        
        # 日本の電話番号フォーマット
        if len(digits) == 10:
            if digits.startswith('0'):
                return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        elif len(digits) == 11:
            if digits.startswith('0'):
                return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        
        return phone
    
    @staticmethod
    def format_product_id(product_id: str) -> str:
        """商品IDをフォーマット"""
        if not product_id:
            return ""
        
        # 大文字に変換し、不要な空白を削除
        return product_id.upper().strip()
    
    @staticmethod
    def format_color_name(color_name: str) -> str:
        """カラー名をフォーマット"""
        if not color_name:
            return ""
        
        # 先頭大文字、残り小文字に変換
        return color_name.strip().title()
    
    @staticmethod
    def format_size_name(size_name: str) -> str:
        """サイズ名をフォーマット"""
        if not size_name:
            return ""
        
        # 大文字に変換
        return size_name.strip().upper()
    
    @staticmethod
    def format_confidence(confidence: float) -> str:
        """信頼度をフォーマット"""
        if confidence is None:
            return ""
        
        return f"{confidence:.2f}"
    
    @staticmethod
    def format_status(status: str) -> str:
        """ステータスをフォーマット"""
        status_map = {
            'pending': '待機中',
            'in_progress': '処理中',
            'completed': '完了',
            'failed': '失敗',
            'cancelled': 'キャンセル'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def format_conversion_type(conversion_type: str) -> str:
        """変換タイプをフォーマット"""
        type_map = {
            'color': 'カラー',
            'size': 'サイズ',
            'composite': '複合',
            'batch': '一括'
        }
        return type_map.get(conversion_type, conversion_type)
    
    @staticmethod
    def format_error_message(error: str, max_length: int = 100) -> str:
        """エラーメッセージをフォーマット"""
        if not error:
            return ""
        
        # 長すぎる場合は省略
        if len(error) > max_length:
            return error[:max_length] + "..."
        
        return error
    
    @staticmethod
    def format_table_data(data: List[Dict], columns: List[str]) -> List[Dict]:
        """テーブルデータをフォーマット"""
        formatted_data = []
        
        for row in data:
            formatted_row = {}
            for col in columns:
                value = row.get(col, "")
                
                # 値の型に応じてフォーマット
                if isinstance(value, datetime):
                    formatted_row[col] = Formatters.format_datetime(value)
                elif isinstance(value, date):
                    formatted_row[col] = Formatters.format_date(value)
                elif isinstance(value, float):
                    if col in ['confidence']:
                        formatted_row[col] = Formatters.format_confidence(value)
                    elif col in ['amount', 'price']:
                        formatted_row[col] = Formatters.format_currency(value)
                    else:
                        formatted_row[col] = f"{value:.2f}"
                elif isinstance(value, str):
                    if col in ['status']:
                        formatted_row[col] = Formatters.format_status(value)
                    elif col in ['conversion_type']:
                        formatted_row[col] = Formatters.format_conversion_type(value)
                    elif col in ['error_message']:
                        formatted_row[col] = Formatters.format_error_message(value)
                    else:
                        formatted_row[col] = value
                else:
                    formatted_row[col] = str(value) if value is not None else ""
            
            formatted_data.append(formatted_row)
        
        return formatted_data
    
    @staticmethod
    def format_sql_query(query: str) -> str:
        """SQLクエリをフォーマット"""
        if not query:
            return ""
        
        # 基本的なSQLフォーマット
        formatted = query.strip()
        
        # キーワードを大文字に変換
        keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END']
        
        for keyword in keywords:
            formatted = re.sub(rf'\b{keyword}\b', keyword, formatted, flags=re.IGNORECASE)
        
        return formatted
