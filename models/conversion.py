"""
変換履歴データモデル
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum

class ConversionStatus(Enum):
    """変換ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConversionType(Enum):
    """変換タイプ"""
    COLOR = "color"
    SIZE = "size"
    COMPOSITE = "composite"
    BATCH = "batch"

@dataclass
class ConversionHistory:
    """変換履歴データクラス"""
    id: Optional[int] = None
    product_id: str = ""
    original_value: str = ""
    converted_color_id: Optional[int] = None
    converted_size_id: Optional[int] = None
    conversion_type: ConversionType = ConversionType.COLOR
    status: ConversionStatus = ConversionStatus.PENDING
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
            'conversion_type': self.conversion_type.value,
            'status': self.status.value,
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
            conversion_type=ConversionType(data.get('conversion_type', 'color')),
            status=ConversionStatus(data.get('status', 'pending')),
            confidence=data.get('confidence', 1.0),
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

@dataclass
class ConversionBatch:
    """変換バッチデータクラス"""
    id: Optional[int] = None
    batch_name: str = ""
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    status: ConversionStatus = ConversionStatus.PENDING
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
            'status': self.status.value,
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
            status=ConversionStatus(data.get('status', 'pending')),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
