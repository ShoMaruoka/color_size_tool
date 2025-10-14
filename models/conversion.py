"""
変換処理関連のデータモデル
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ConversionRule:
    """変換ルールクラス"""
    id: Optional[int] = None
    source_name: str = ""
    target_id: int = 0
    target_name: str = ""
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
            'source_name': self.source_name,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'confidence': self.confidence,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversionRule':
        """辞書からインスタンスを作成"""
        return cls(
            id=data.get('id'),
            source_name=data.get('source_name', ''),
            target_id=data.get('target_id', 0),
            target_name=data.get('target_name', ''),
            confidence=data.get('confidence', 1.0),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ConversionHistory:
    """変換履歴クラス"""
    id: Optional[int] = None
    product_id: str = ""
    original_value: str = ""
    converted_color_id: Optional[int] = None
    converted_size_id: Optional[int] = None
    conversion_type: str = ""
    status: str = ""
    confidence: float = 1.0
    error_message: Optional[str] = None
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
            'product_id': self.product_id,
            'original_value': self.original_value,
            'converted_color_id': self.converted_color_id,
            'converted_size_id': self.converted_size_id,
            'conversion_type': self.conversion_type,
            'status': self.status,
            'confidence': self.confidence,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversionHistory':
        """辞書からインスタンスを作成"""
        return cls(
            id=data.get('id'),
            product_id=data.get('product_id', ''),
            original_value=data.get('original_value', ''),
            converted_color_id=data.get('converted_color_id'),
            converted_size_id=data.get('converted_size_id'),
            conversion_type=data.get('conversion_type', ''),
            status=data.get('status', ''),
            confidence=data.get('confidence', 1.0),
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ConversionBatch:
    """変換バッチクラス"""
    id: Optional[int] = None
    batch_name: str = ""
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
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
            'batch_name': self.batch_name,
            'total_records': self.total_records,
            'processed_records': self.processed_records,
            'successful_records': self.successful_records,
            'failed_records': self.failed_records,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversionBatch':
        """辞書からインスタンスを作成"""
        return cls(
            id=data.get('id'),
            batch_name=data.get('batch_name', ''),
            total_records=data.get('total_records', 0),
            processed_records=data.get('processed_records', 0),
            successful_records=data.get('successful_records', 0),
            failed_records=data.get('failed_records', 0),
            status=data.get('status', 'pending'),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ConversionResult:
    """変換結果クラス"""
    product_id: str
    original_color_name: Optional[str] = None
    original_size_name: Optional[str] = None
    original_composite_value: Optional[str] = None
    converted_color_id: Optional[int] = None
    converted_color_name: Optional[str] = None
    converted_size_id: Optional[int] = None
    converted_size_name: Optional[str] = None
    confidence: float = 0.0
    conversion_type: str = "auto"
    status: str = "pending"
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'product_id': self.product_id,
            'original_color_name': self.original_color_name,
            'original_size_name': self.original_size_name,
            'original_composite_value': self.original_composite_value,
            'converted_color_id': self.converted_color_id,
            'converted_color_name': self.converted_color_name,
            'converted_size_id': self.converted_size_id,
            'converted_size_name': self.converted_size_name,
            'confidence': self.confidence,
            'conversion_type': self.conversion_type,
            'status': self.status,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversionResult':
        """辞書からインスタンスを作成"""
        return cls(
            product_id=data.get('product_id', ''),
            original_color_name=data.get('original_color_name'),
            original_size_name=data.get('original_size_name'),
            original_composite_value=data.get('original_composite_value'),
            converted_color_id=data.get('converted_color_id'),
            converted_color_name=data.get('converted_color_name'),
            converted_size_id=data.get('converted_size_id'),
            converted_size_name=data.get('converted_size_name'),
            confidence=data.get('confidence', 0.0),
            conversion_type=data.get('conversion_type', 'auto'),
            status=data.get('status', 'pending'),
            error_message=data.get('error_message')
        )