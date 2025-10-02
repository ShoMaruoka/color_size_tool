"""
ヘルパー関数
"""
import os
import sys
from typing import Any, List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
import pandas as pd

def get_project_root() -> str:
    """プロジェクトルートディレクトリを取得"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(current_dir))

def ensure_directory_exists(directory_path: str) -> None:
    """ディレクトリが存在しない場合は作成"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

def get_data_directory() -> str:
    """データディレクトリのパスを取得"""
    project_root = get_project_root()
    data_dir = os.path.join(project_root, 'data')
    ensure_directory_exists(data_dir)
    return data_dir

def get_logs_directory() -> str:
    """ログディレクトリのパスを取得"""
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    ensure_directory_exists(logs_dir)
    return logs_dir

def safe_int(value: Any, default: int = 0) -> int:
    """安全に整数に変換"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """安全に浮動小数点に変換"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """安全に文字列に変換"""
    if value is None:
        return default
    return str(value).strip()

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """リストを指定サイズのチャンクに分割"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(lst: List[List[Any]]) -> List[Any]:
    """ネストしたリストを平坦化"""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """リストから重複を削除（順序を保持）"""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def get_date_range(days: int = 30, end_date: Optional[date] = None) -> Tuple[date, date]:
    """日付範囲を取得"""
    if end_date is None:
        end_date = date.today()
    
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def is_valid_date_range(start_date: date, end_date: date) -> bool:
    """有効な日付範囲かチェック"""
    return start_date <= end_date

def calculate_percentage(part: int, total: int) -> float:
    """パーセンテージを計算"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def format_elapsed_time(start_time: datetime, end_time: Optional[datetime] = None) -> str:
    """経過時間をフォーマット"""
    if end_time is None:
        end_time = datetime.now()
    
    elapsed = end_time - start_time
    total_seconds = int(elapsed.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}時間{minutes}分{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分{seconds}秒"
    else:
        return f"{seconds}秒"

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """プログレスバーを作成"""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    percentage = current / total
    filled_width = int(width * percentage)
    bar = "█" * filled_width + "░" * (width - filled_width)
    return f"[{bar}] {percentage:.1%}"

def safe_get_dict_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """辞書から安全に値を取得"""
    return data.get(key, default)

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """複数の辞書をマージ"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def filter_dict_by_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """指定されたキーのみで辞書をフィルタ"""
    return {key: data[key] for key in keys if key in data}

def convert_dataframe_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """DataFrameを辞書のリストに変換"""
    return df.to_dict('records')

def convert_dict_list_to_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """辞書のリストをDataFrameに変換"""
    return pd.DataFrame(data)

def get_file_extension(filename: str) -> str:
    """ファイル拡張子を取得"""
    return os.path.splitext(filename)[1].lower()

def is_valid_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """有効なファイル拡張子かチェック"""
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def get_file_size_mb(filepath: str) -> float:
    """ファイルサイズをMBで取得"""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """文字列を指定長で切り詰め"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def normalize_whitespace(text: str) -> str:
    """空白文字を正規化"""
    import re
    return re.sub(r'\s+', ' ', text.strip())

def extract_numbers(text: str) -> List[int]:
    """文字列から数値を抽出"""
    import re
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def is_empty_or_none(value: Any) -> bool:
    """値が空またはNoneかチェック"""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False

def get_system_info() -> Dict[str, str]:
    """システム情報を取得"""
    import platform
    
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }
