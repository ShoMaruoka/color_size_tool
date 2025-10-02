"""
エラーハンドリング機能
"""
import traceback
from typing import Any, Dict, Optional, Callable
from functools import wraps
import streamlit as st

from ..config.logging_config import app_logger

class AppError(Exception):
    """アプリケーション固有のエラー"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class DatabaseError(AppError):
    """データベース関連のエラー"""
    pass

class ValidationError(AppError):
    """バリデーション関連のエラー"""
    pass

class ConversionError(AppError):
    """変換処理関連のエラー"""
    pass

class ConfigurationError(AppError):
    """設定関連のエラー"""
    pass

def handle_exceptions(
    show_error_in_ui: bool = True,
    log_error: bool = True,
    return_default: Any = None
):
    """例外ハンドリングデコレータ"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AppError as e:
                if log_error:
                    app_logger.error(f"アプリケーションエラー: {e.message}", extra=e.details)
                
                if show_error_in_ui:
                    st.error(f"❌ {e.message}")
                    if e.details:
                        with st.expander("詳細情報"):
                            st.json(e.details)
                
                return return_default
                
            except Exception as e:
                error_msg = f"予期しないエラーが発生しました: {str(e)}"
                
                if log_error:
                    app_logger.error(f"予期しないエラー: {error_msg}")
                    app_logger.error(f"スタックトレース: {traceback.format_exc()}")
                
                if show_error_in_ui:
                    st.error(f"❌ {error_msg}")
                    with st.expander("技術的詳細"):
                        st.code(traceback.format_exc())
                
                return return_default
        
        return wrapper
    return decorator

def safe_execute(
    func: Callable,
    *args,
    show_error_in_ui: bool = True,
    log_error: bool = True,
    return_default: Any = None,
    **kwargs
) -> Any:
    """安全に関数を実行"""
    try:
        return func(*args, **kwargs)
    except AppError as e:
        if log_error:
            app_logger.error(f"アプリケーションエラー: {e.message}", extra=e.details)
        
        if show_error_in_ui:
            st.error(f"❌ {e.message}")
            if e.details:
                with st.expander("詳細情報"):
                    st.json(e.details)
        
        return return_default
        
    except Exception as e:
        error_msg = f"予期しないエラーが発生しました: {str(e)}"
        
        if log_error:
            app_logger.error(f"予期しないエラー: {error_msg}")
            app_logger.error(f"スタックトレース: {traceback.format_exc()}")
        
        if show_error_in_ui:
            st.error(f"❌ {error_msg}")
            with st.expander("技術的詳細"):
                st.code(traceback.format_exc())
        
        return return_default

class ErrorHandler:
    """エラーハンドラークラス"""
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
    
    def handle_error(
        self,
        error: Exception,
        context: str = "",
        show_in_ui: bool = True,
        log_error: bool = True
    ) -> None:
        """エラーを処理"""
        self.error_count += 1
        
        error_info = {
            'timestamp': str(traceback.format_exc()),
            'context': context,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'count': self.error_count
        }
        
        self.error_history.append(error_info)
        
        if log_error:
            app_logger.error(f"エラー発生 [{context}]: {str(error)}")
            app_logger.error(f"スタックトレース: {traceback.format_exc()}")
        
        if show_in_ui:
            if isinstance(error, AppError):
                st.error(f"❌ {error.message}")
                if error.details:
                    with st.expander("詳細情報"):
                        st.json(error.details)
            else:
                st.error(f"❌ 予期しないエラーが発生しました: {str(error)}")
                with st.expander("技術的詳細"):
                    st.code(traceback.format_exc())
    
    def get_error_summary(self) -> Dict[str, Any]:
        """エラーサマリーを取得"""
        return {
            'total_errors': self.error_count,
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'error_types': self._get_error_type_counts()
        }
    
    def _get_error_type_counts(self) -> Dict[str, int]:
        """エラータイプ別のカウントを取得"""
        type_counts = {}
        for error_info in self.error_history:
            error_type = error_info['error_type']
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
        return type_counts
    
    def clear_history(self) -> None:
        """エラー履歴をクリア"""
        self.error_history.clear()
        self.error_count = 0

def validate_database_connection(func: Callable):
    """データベース接続のバリデーション"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "connection" in str(e).lower() or "database" in str(e).lower():
                raise DatabaseError(
                    "データベース接続エラーが発生しました",
                    error_code="DB_CONNECTION_ERROR",
                    details={'original_error': str(e)}
                )
            raise
    return wrapper

def validate_input_data(func: Callable):
    """入力データのバリデーション"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            raise ValidationError(
                f"入力データが無効です: {str(e)}",
                error_code="VALIDATION_ERROR",
                details={'original_error': str(e)}
            )
        except TypeError as e:
            raise ValidationError(
                f"データ型が無効です: {str(e)}",
                error_code="TYPE_ERROR",
                details={'original_error': str(e)}
            )
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """失敗時のリトライ機能"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        app_logger.warning(f"試行 {attempt + 1} 失敗、{delay}秒後にリトライ: {str(e)}")
                        import time
                        time.sleep(delay)
                    else:
                        app_logger.error(f"最大試行回数 {max_retries} に達しました")
            
            raise last_exception
        
        return wrapper
    return decorator

# グローバルエラーハンドラーインスタンス
global_error_handler = ErrorHandler()
