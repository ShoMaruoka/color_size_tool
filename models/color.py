"""
カラーデータモデル
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Color:
    """カラーデータクラス"""
    color_id: int
    color_name: str
    color_code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
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
            'color_id': self.color_id,
            'color_name': self.color_name,
            'color_code': self.color_code,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Color':
        """辞書からインスタンスを作成"""
        return cls(
            color_id=data.get('color_id', 0),
            color_name=data.get('color_name', ''),
            color_code=data.get('color_code'),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ColorConversionRule:
    """カラー変換ルールクラス"""
    id: Optional[int] = None
    source_color_name: str = ""
    target_color_id: int = 0
    target_color_name: str = ""
    confidence: float = 1.0
    is_active: bool = True
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
            'id': self.id,
            'source_color_name': self.source_color_name,
            'target_color_id': self.target_color_id,
            'target_color_name': self.target_color_name,
            'confidence': self.confidence,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ColorConversionRule':
        """辞書からインスタンスを作成"""
        return cls(
            id=data.get('id'),
            source_color_name=data.get('source_color_name', ''),
            target_color_id=data.get('target_color_id', 0),
            target_color_name=data.get('target_color_name', ''),
            confidence=data.get('confidence', 1.0),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
