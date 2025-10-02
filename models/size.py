"""
サイズデータモデル
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Size:
    """サイズデータクラス"""
    size_id: int
    size_name: str
    size_code: Optional[str] = None
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
            'size_id': self.size_id,
            'size_name': self.size_name,
            'size_code': self.size_code,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Size':
        """辞書からインスタンスを作成"""
        return cls(
            size_id=data.get('size_id', 0),
            size_name=data.get('size_name', ''),
            size_code=data.get('size_code'),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class SizeConversionRule:
    """サイズ変換ルールクラス"""
    id: Optional[int] = None
    source_size_name: str = ""
    target_size_id: int = 0
    target_size_name: str = ""
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
            'source_size_name': self.source_size_name,
            'target_size_id': self.target_size_id,
            'target_size_name': self.target_size_name,
            'confidence': self.confidence,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SizeConversionRule':
        """辞書からインスタンスを作成"""
        return cls(
            id=data.get('id'),
            source_size_name=data.get('source_size_name', ''),
            target_size_id=data.get('target_size_id', 0),
            target_size_name=data.get('target_size_name', ''),
            confidence=data.get('confidence', 1.0),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
