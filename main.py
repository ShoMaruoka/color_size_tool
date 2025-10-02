"""
カラーサイズメンテナンスツール メインアプリケーション
"""
import streamlit as st
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.logging_config import app_logger
from utils.error_handlers import handle_exceptions, global_error_handler

def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="カラーサイズメンテナンスツール",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # アプリケーション初期化
    initialize_app()
    
    # サイドバーナビゲーション
    show_sidebar_navigation()
    
    # メインコンテンツ
    show_main_content()

@handle_exceptions(show_error_in_ui=True, log_error=True)
def initialize_app():
    """アプリケーション初期化"""
    # セッション状態の初期化
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = "ホーム"
        st.session_state.retrieved_data = []
        st.session_state.conversion_rules = []
        
        app_logger.info("アプリケーションが初期化されました")

def show_sidebar_navigation():
    """サイドバーナビゲーション"""
    with st.sidebar:
        st.title("🎨 カラーサイズメンテナンスツール")
        st.markdown("---")
        
        # ナビゲーションメニュー
        pages = {
            "🏠 ホーム": "ホーム",
            "📊 データ取得": "データ取得",
            "🔄 変換処理": "変換処理",
            "📋 変換表管理": "変換表管理",
            "💾 データ登録": "データ登録",
            "⚙️ 設定": "設定"
        }
        
        selected_page = st.radio(
            "メニュー",
            list(pages.keys()),
            index=list(pages.values()).index(st.session_state.get('current_page', 'ホーム'))
        )
        
        st.session_state.current_page = pages[selected_page]
        
        st.markdown("---")
        
        # アプリケーション情報
        st.markdown("### 📋 アプリケーション情報")
        st.info("**バージョン**: 1.0.0\n\n**開発フェーズ**: Phase 1\n\n**ステータス**: 開発中")
        
        # エラー情報
        if global_error_handler.error_count > 0:
            st.markdown("### ⚠️ エラー情報")
            error_summary = global_error_handler.get_error_summary()
            st.warning(f"エラー数: {error_summary['total_errors']}")
            
            if st.button("エラー履歴をクリア"):
                global_error_handler.clear_history()
                st.rerun()

def show_main_content():
    """メインコンテンツ表示"""
    current_page = st.session_state.get('current_page', 'ホーム')
    
    if current_page == "ホーム":
        show_home_page()
    elif current_page == "データ取得":
        show_data_retrieval_page()
    elif current_page == "変換処理":
        show_conversion_page()
    elif current_page == "変換表管理":
        show_conversion_table_page()
    elif current_page == "データ登録":
        show_data_registration_page()
    elif current_page == "設定":
        show_settings_page()

def show_home_page():
    """ホームページ"""
    st.title("🎨 カラーサイズメンテナンスツール")
    st.markdown("---")
    
    # アプリケーション概要
    st.markdown("### 📋 アプリケーション概要")
    st.info("""
    このツールは商品データのカラー名とサイズ名をIDに変換するためのメンテナンスツールです。
    
    **主な機能:**
    - 📊 データベースからの商品データ取得
    - 🔄 カラー名・サイズ名のID変換処理
    - 📋 変換ルールの管理
    - 💾 変換結果のデータベース登録
    """)
    
    # 開発状況
    st.markdown("### 🚧 開発状況")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Phase 1: 環境構築・基盤開発")
        st.success("✅ 完了")
        st.markdown("- 開発環境構築")
        st.markdown("- 基盤モジュール実装")
        st.markdown("- 基本UI構築")
    
    with col2:
        st.markdown("#### Phase 2: データ取得機能")
        st.info("🔄 準備中")
        st.markdown("- データベース接続機能")
        st.markdown("- データ取得機能")
        st.markdown("- データ取得画面")
    
    with col3:
        st.markdown("#### Phase 3: 変換処理機能")
        st.info("⏳ 未開始")
        st.markdown("- 変換表管理機能")
        st.markdown("- 自動変換機能")
        st.markdown("- 手動設定機能")
    
    # クイックアクション
    st.markdown("### ⚡ クイックアクション")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 データ取得を開始", use_container_width=True):
            st.session_state.current_page = "データ取得"
            st.rerun()
    
    with col2:
        if st.button("📋 変換表を管理", use_container_width=True):
            st.session_state.current_page = "変換表管理"
            st.rerun()
    
    with col3:
        if st.button("⚙️ 設定を確認", use_container_width=True):
            st.session_state.current_page = "設定"
            st.rerun()

def show_data_retrieval_page():
    """データ取得ページ"""
    try:
        from pages.data_retrieval import show_data_retrieval_page
        show_data_retrieval_page()
    except ImportError as e:
        st.error(f"データ取得ページのモジュールが見つかりません: {e}")
        st.info("Phase 2で実装予定です")

def show_conversion_page():
    """変換処理ページ"""
    st.title("🔄 変換処理")
    st.markdown("---")
    st.info("Phase 3で実装予定です")

def show_conversion_table_page():
    """変換表管理ページ"""
    st.title("📋 変換表管理")
    st.markdown("---")
    st.info("Phase 3で実装予定です")

def show_data_registration_page():
    """データ登録ページ"""
    st.title("💾 データ登録")
    st.markdown("---")
    st.info("Phase 4で実装予定です")

def show_settings_page():
    """設定ページ"""
    st.title("⚙️ 設定")
    st.markdown("---")
    
    # データベース設定
    st.markdown("### 🗄️ データベース設定")
    
    db_type = st.selectbox(
        "データベースタイプ",
        ["sqlite", "sqlserver", "mariadb"],
        help="使用するデータベースのタイプを選択してください"
    )
    
    if db_type == "sqlite":
        st.info("SQLiteは設定不要です。data/conversion.dbが使用されます。")
    else:
        st.warning(f"{db_type}の設定は.envファイルで行ってください")
    
    # アプリケーション設定
    st.markdown("### 🔧 アプリケーション設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        debug_mode = st.checkbox("デバッグモード", value=False)
        auto_convert = st.checkbox("自動変換を有効化", value=True)
    
    with col2:
        backup_enabled = st.checkbox("変換前にバックアップ", value=True)
        validation_enabled = st.checkbox("変換後に検証", value=True)
    
    # ログ設定
    st.markdown("### 📝 ログ設定")
    
    log_level = st.selectbox(
        "ログレベル",
        ["DEBUG", "INFO", "WARNING", "ERROR"],
        index=1
    )
    
    if st.button("設定を保存"):
        st.success("設定が保存されました")
        app_logger.info("アプリケーション設定が更新されました")

if __name__ == "__main__":
    main()
