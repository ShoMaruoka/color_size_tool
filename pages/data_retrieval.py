"""
データ取得ページ
"""
import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd

from services.database_service import DatabaseService
from services.data_service import DataService
from config.database import DatabaseConfig
from config.logging_config import app_logger
from models.product import ProductFilter
from utils.helpers import get_date_range

def show_data_retrieval_page():
    """データ取得ページを表示"""
    st.title("📊 データ取得")
    st.markdown("---")
    
    # サイドバーでデータベース接続設定
    with st.sidebar:
        st.header("🔧 データベース設定")
        
        db_type = st.selectbox(
            "データベースタイプ",
            ["sqlite", "sqlserver", "mariadb"],
            help="接続するデータベースのタイプを選択してください"
        )
        
        # 接続設定の詳細表示
        show_connection_settings(db_type)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("接続テスト", type="primary", use_container_width=True):
                test_database_connection(db_type)
        
        with col2:
            if st.button("設定検証", use_container_width=True):
                validate_connection_settings(db_type)
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📅 期間設定")
        
        # 期間選択
        date_option = st.radio(
            "期間選択方法",
            ["過去N日間", "カスタム期間"],
            horizontal=True
        )
        
        if date_option == "過去N日間":
            days = st.slider("過去何日間", 1, 365, 30)
            start_date, end_date = get_date_range(days)
            st.info(f"期間: {start_date} ～ {end_date}")
        else:
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input("開始日", value=date.today() - timedelta(days=30))
            with col_end:
                end_date = st.date_input("終了日", value=date.today())
    
    with col2:
        st.header("🔍 フィルター設定")
        
        # 商品名フィルター
        product_name_pattern = st.text_input(
            "商品名パターン",
            placeholder="例: Tシャツ*",
            help="商品名の検索パターンを入力（*はワイルドカード）"
        )
        
        # カラー名フィルター
        color_name_pattern = st.text_input(
            "カラー名パターン",
            placeholder="例: 赤*",
            help="カラー名の検索パターンを入力"
        )
        
        # サイズ名フィルター
        size_name_pattern = st.text_input(
            "サイズ名パターン",
            placeholder="例: M*",
            help="サイズ名の検索パターンを入力"
        )
        
        # 変換状況フィルター
        has_color_id = st.selectbox(
            "カラーID変換状況",
            ["すべて", "変換済み", "未変換"],
            help="カラーIDの変換状況でフィルター"
        )
        
        has_size_id = st.selectbox(
            "サイズID変換状況",
            ["すべて", "変換済み", "未変換"],
            help="サイズIDの変換状況でフィルター"
        )
    
    # データ取得ボタン
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 データ取得", type="primary", use_container_width=True):
            retrieve_data(
                db_type, start_date, end_date,
                product_name_pattern, color_name_pattern, size_name_pattern,
                has_color_id, has_size_id
            )
    
    with col2:
        if st.button("📊 統計情報", use_container_width=True):
            show_statistics(db_type, start_date, end_date)
    
    with col3:
        st.info("💡 データ取得後、変換処理ページで変換作業を行えます")

def test_database_connection(db_type: str):
    """データベース接続をテスト"""
    try:
        with st.spinner("データベース接続をテスト中..."):
            db_service = DatabaseService()
            success = db_service.test_connection(db_type)
            
            if success:
                st.success(f"✅ {db_type}への接続が成功しました")
            else:
                st.error(f"❌ {db_type}への接続に失敗しました")
                
    except Exception as e:
        st.error(f"❌ 接続テスト中にエラーが発生しました: {str(e)}")
        app_logger.error(f"データベース接続テストエラー: {e}")

def retrieve_data(
    db_type: str, start_date: date, end_date: date,
    product_name_pattern: str, color_name_pattern: str, size_name_pattern: str,
    has_color_id: str, has_size_id: str
):
    """データを取得"""
    try:
        with st.spinner("データを取得中..."):
            # データサービスを初期化
            data_service = DataService()
            
            # フィルター条件を構築
            product_filter = ProductFilter(
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.max.time()),
                product_name_pattern=product_name_pattern if product_name_pattern else None,
                color_name_pattern=color_name_pattern if color_name_pattern else None,
                size_name_pattern=size_name_pattern if size_name_pattern else None,
                has_color_id=_convert_filter_option(has_color_id),
                has_size_id=_convert_filter_option(has_size_id),
                limit=1000  # 表示件数制限
            )
            
            # データ取得
            if db_type == 'sqlite':
                # SQLiteの場合はサンプルデータを使用
                products = data_service.get_sample_products()
            else:
                # 実際のデータベースから取得
                products = data_service.get_products(product_filter, db_type)
            
            # セッション状態に保存
            st.session_state['retrieved_data'] = [product.to_dict() for product in products]
            st.session_state['product_filter'] = product_filter
            st.session_state['db_type'] = db_type
            
            st.success(f"✅ {len(products)}件のデータを取得しました")
            
            # データプレビューを表示
            show_data_preview([product.to_dict() for product in products])
            
    except Exception as e:
        st.error(f"❌ データ取得中にエラーが発生しました: {str(e)}")
        app_logger.error(f"データ取得エラー: {e}")

def show_statistics(db_type: str, start_date: date, end_date: date):
    """統計情報を表示"""
    try:
        with st.spinner("統計情報を取得中..."):
            # データサービスを初期化
            data_service = DataService()
            
            # フィルター条件を構築
            product_filter = ProductFilter(
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.max.time())
            )
            
            # 統計情報を取得
            if db_type == 'sqlite':
                # SQLiteの場合はサンプルデータから統計を計算
                products = data_service.get_sample_products()
                stats = _calculate_sample_statistics(products)
            else:
                # 実際のデータベースから統計を取得
                stats = data_service.get_product_statistics(product_filter, db_type)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("総商品数", f"{stats['total_products']:,}")
            
            with col2:
                st.metric("カラー変換済み", f"{stats['converted_colors']:,}")
            
            with col3:
                st.metric("サイズ変換済み", f"{stats['converted_sizes']:,}")
            
            with col4:
                st.metric("変換率", f"{stats['conversion_rate']:.1%}")
            
            # グラフ表示
            st.subheader("📈 変換状況")
            
            chart_data = pd.DataFrame({
                'カテゴリ': ['カラー変換済み', 'サイズ変換済み', '未変換'],
                '件数': [stats['converted_colors'], stats['converted_sizes'], stats['pending_conversions']]
            })
            
            st.bar_chart(chart_data.set_index('カテゴリ'))
            
    except Exception as e:
        st.error(f"❌ 統計情報取得中にエラーが発生しました: {str(e)}")
        app_logger.error(f"統計情報取得エラー: {e}")

def show_data_preview(data: list):
    """データプレビューを表示"""
    st.subheader("📋 データプレビュー")
    
    if not data:
        st.warning("データがありません")
        return
    
    # DataFrameに変換
    df = pd.DataFrame(data)
    
    # 表示件数制限
    max_rows = 100
    if len(df) > max_rows:
        st.info(f"表示件数を{max_rows}件に制限しています（全{len(df)}件）")
        df = df.head(max_rows)
    
    # テーブル表示
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # ダウンロードボタン
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSVダウンロード",
        data=csv,
        file_name=f"product_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def _calculate_sample_statistics(products) -> dict:
    """サンプルデータから統計を計算"""
    total = len(products)
    converted_colors = sum(1 for p in products if p.color_id is not None)
    converted_sizes = sum(1 for p in products if p.size_id is not None)
    pending = sum(1 for p in products if p.color_id is None and p.size_id is None)
    
    conversion_rate = (converted_colors + converted_sizes) / (total * 2) if total > 0 else 0.0
    
    return {
        'total_products': total,
        'converted_colors': converted_colors,
        'converted_sizes': converted_sizes,
        'pending_conversions': pending,
        'conversion_rate': conversion_rate
    }

def show_connection_settings(db_type: str):
    """接続設定を表示"""
    try:
        data_service = DataService()
        config = data_service.db_service.config
        
        if db_type == 'sqlite':
            st.info("📁 SQLite設定")
            st.text(f"データベース: {config.sqlite_config['database']}")
            st.success("✅ SQLiteは設定不要です")
            
        elif db_type == 'sqlserver':
            st.info("🗄️ SQL Server設定")
            config_data = config.sqlserver_config
            st.text(f"サーバー: {config_data['server']}")
            st.text(f"データベース: {config_data['database']}")
            st.text(f"ドライバー: {config_data['driver']}")
            
            if config_data['trusted_connection'] == 'yes':
                st.text("認証: Windows認証")
            else:
                st.text(f"ユーザー: {config_data['uid']}")
                st.text("認証: SQL認証")
                
        elif db_type == 'mariadb':
            st.info("🐬 MariaDB設定")
            config_data = config.mariadb_config
            st.text(f"ホスト: {config_data['host']}:{config_data['port']}")
            st.text(f"データベース: {config_data['database']}")
            st.text(f"ユーザー: {config_data['user']}")
            
        # 設定検証結果を表示
        validation_result = data_service.validate_connection_settings(db_type)
        if validation_result['is_valid']:
            st.success("✅ " + validation_result['message'])
        else:
            st.error("❌ " + validation_result['message'])
            if 'missing_fields' in validation_result:
                st.warning(f"不足項目: {', '.join(validation_result['missing_fields'])}")
                
    except Exception as e:
        st.error(f"❌ 設定表示エラー: {str(e)}")
        app_logger.error(f"接続設定表示エラー: {e}")

def validate_connection_settings(db_type: str):
    """接続設定を検証"""
    try:
        data_service = DataService()
        validation_result = data_service.validate_connection_settings(db_type)
        
        if validation_result['is_valid']:
            st.success("✅ " + validation_result['message'])
        else:
            st.error("❌ " + validation_result['message'])
            if 'missing_fields' in validation_result:
                st.warning(f"不足項目: {', '.join(validation_result['missing_fields'])}")
                
    except Exception as e:
        st.error(f"❌ 設定検証エラー: {str(e)}")
        app_logger.error(f"接続設定検証エラー: {e}")

def _convert_filter_option(option: str) -> bool:
    """フィルターオプションを変換"""
    if option == "変換済み":
        return True
    elif option == "未変換":
        return False
    else:
        return None
