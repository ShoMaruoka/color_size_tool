"""
商品データモデル
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    """商品データクラス"""
    product_id: str
    product_name: str
    color_name: Optional[str] = None
    size_name: Optional[str] = None
    composite_value: Optional[str] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'color_name': self.color_name,
            'size_name': self.size_name,
            'composite_value': self.composite_value,
            'color_id': self.color_id,
            'size_id': self.size_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """辞書からインスタンスを作成"""
        return cls(
            product_id=data.get('product_id', ''),
            product_name=data.get('product_name', ''),
            color_name=data.get('color_name'),
            size_name=data.get('size_name'),
            composite_value=data.get('composite_value'),
            color_id=data.get('color_id'),
            size_id=data.get('size_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ProductFilter:
    """商品フィルタークラス"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    product_name_pattern: Optional[str] = None
    color_name_pattern: Optional[str] = None
    size_name_pattern: Optional[str] = None
    has_color_id: Optional[bool] = None
    has_size_id: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'product_name_pattern': self.product_name_pattern,
            'color_name_pattern': self.color_name_pattern,
            'size_name_pattern': self.size_name_pattern,
            'has_color_id': self.has_color_id,
            'has_size_id': self.has_size_id,
            'limit': self.limit,
            'offset': self.offset
        }
