"""
データ登録ページ
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import time

from services.insert_service import InsertService
from services.database_service import DatabaseService
from models.product import Product
from config.logging_config import app_logger
from utils.error_handlers import handle_exceptions

def show_data_registration_page():
    """データ登録ページを表示"""
    st.title("💾 データ登録")
    st.markdown("---")
    
    # セッション状態の初期化
    if 'insert_service' not in st.session_state:
        st.session_state.insert_service = InsertService()
    if 'db_service' not in st.session_state:
        st.session_state.db_service = DatabaseService()
    
    # タブで機能を分割
    tab1, tab2, tab3 = st.tabs(["📊 登録対象確認", "🔍 データ検証", "🚀 登録実行"])
    
    with tab1:
        show_registration_targets()
    
    with tab2:
        show_data_validation()
    
    with tab3:
        show_registration_execution()

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_registration_targets():
    """登録対象確認"""
    st.header("📊 登録対象データ確認")
    
    # 変換済みデータの確認
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 登録対象のデータがありません")
        st.info("💡 データ取得ページでデータを取得し、変換処理ページで変換を行ってから登録してください")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 データ取得ページに移動"):
                st.session_state.current_page = "データ取得"
                st.rerun()
        with col2:
            if st.button("🔄 変換処理ページに移動"):
                st.session_state.current_page = "変換処理"
                st.rerun()
        return
    
    # データの表示
    data = st.session_state.retrieved_data
    df = pd.DataFrame(data)
    
    st.subheader(f"📋 登録対象データ ({len(data)}件)")
    
    # 登録準備状況の統計
    insert_service = st.session_state.insert_service
    products = [Product.from_dict(item) for item in data]
    summary = insert_service.get_insert_summary(products)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総商品数", f"{summary['total_products']:,}")
    
    with col2:
        st.metric("カラー準備済み", f"{summary['color_ready']:,}", f"{summary['color_percentage']:.1f}%")
    
    with col3:
        st.metric("サイズ準備済み", f"{summary['size_ready']:,}", f"{summary['size_percentage']:.1f}%")
    
    with col4:
        st.metric("登録準備完了", f"{summary['ready_for_insert']:,}")
    
    # 登録準備状況の詳細
    st.subheader("📈 登録準備状況")
    
    if summary['needs_attention'] > 0:
        st.warning(f"⚠️ {summary['needs_attention']}件のデータで変換が未完了です")
        
        # 未変換データの表示
        incomplete_data = df[(df['color_id'].isna()) | (df['size_id'].isna())]
        if not incomplete_data.empty:
            st.write("**未変換データ:**")
            st.dataframe(
                incomplete_data[['product_id', 'product_name', 'color_name', 'size_name', 'color_id', 'size_id']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.success("✅ すべてのデータが登録準備完了です")
    
    # データベース設定
    st.subheader("🗄️ 登録先データベース設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        db_type = st.selectbox(
            "データベースタイプ",
            ["sqlite", "sqlserver", "mariadb"],
            help="データを登録するデータベースのタイプを選択"
        )
    
    with col2:
        if st.button("🔧 サンプルテーブルを作成", help="テスト用のテーブルを作成"):
            with st.spinner("サンプルテーブルを作成中..."):
                try:
                    insert_service.create_sample_tables(db_type)
                    st.success("✅ サンプルテーブルの作成が完了しました")
                except Exception as e:
                    st.error(f"❌ テーブル作成エラー: {e}")
    
    # 既存データの確認
    if st.button("📊 既存データを確認"):
        with st.spinner("既存データを確認中..."):
            try:
                existing_data = insert_service.get_existing_data(db_type)
                
                st.subheader("📋 既存データ状況")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("既存カラーデータ", f"{existing_data['color_count']:,}件")
                    if existing_data['recent_colors']:
                        st.write("**最新のカラーデータ:**")
                        recent_colors_df = pd.DataFrame(existing_data['recent_colors'])
                        st.dataframe(recent_colors_df, use_container_width=True, hide_index=True)
                
                with col2:
                    st.metric("既存サイズデータ", f"{existing_data['size_count']:,}件")
                    if existing_data['recent_sizes']:
                        st.write("**最新のサイズデータ:**")
                        recent_sizes_df = pd.DataFrame(existing_data['recent_sizes'])
                        st.dataframe(recent_sizes_df, use_container_width=True, hide_index=True)
                        
            except Exception as e:
                st.error(f"❌ 既存データ確認エラー: {e}")

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_data_validation():
    """データ検証"""
    st.header("🔍 データ検証")
    
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 検証対象のデータがありません")
        return
    
    # データ検証の実行
    if st.button("🔍 データ検証を実行", type="primary"):
        with st.spinner("データ検証を実行中..."):
            try:
                data = st.session_state.retrieved_data
                products = [Product.from_dict(item) for item in data]
                
                insert_service = st.session_state.insert_service
                validation_result = insert_service.validate_insert_data(products)
                
                # 検証結果の表示
                st.subheader("📊 検証結果")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("総件数", f"{validation_result['total_count']:,}")
                
                with col2:
                    st.metric("有効データ", f"{validation_result['valid_count']:,}", 
                             delta=f"{validation_result['valid_count']/validation_result['total_count']*100:.1f}%" if validation_result['total_count'] > 0 else "0%")
                
                with col3:
                    st.metric("無効データ", f"{validation_result['invalid_count']:,}", 
                             delta=f"-{validation_result['invalid_count']/validation_result['total_count']*100:.1f}%" if validation_result['total_count'] > 0 else "0%")
                
                # 検証結果の詳細
                if validation_result['is_valid']:
                    st.success("✅ すべてのデータが有効です")
                else:
                    st.error("❌ 無効なデータが含まれています")
                
                # エラーの詳細表示
                if validation_result['errors']:
                    st.subheader("❌ エラー詳細")
                    error_df = pd.DataFrame({
                        'エラー内容': validation_result['errors']
                    })
                    st.dataframe(error_df, use_container_width=True, hide_index=True)
                
                # 警告の詳細表示
                if validation_result['warnings']:
                    st.subheader("⚠️ 警告詳細")
                    warning_df = pd.DataFrame({
                        '警告内容': validation_result['warnings']
                    })
                    st.dataframe(warning_df, use_container_width=True, hide_index=True)
                
                # セッション状態に保存
                st.session_state['validation_result'] = validation_result
                
            except Exception as e:
                st.error(f"❌ データ検証エラー: {e}")
                app_logger.error(f"データ検証エラー: {e}")

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_registration_execution():
    """登録実行"""
    st.header("🚀 データ登録実行")
    
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 登録対象のデータがありません")
        return
    
    # 登録設定
    st.subheader("⚙️ 登録設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        insert_colors = st.checkbox("カラーデータを登録", value=True, help="tm9030colorテーブルに登録")
        insert_sizes = st.checkbox("サイズデータを登録", value=True, help="tm9035sizeテーブルに登録")
    
    with col2:
        db_type = st.selectbox(
            "登録先データベース",
            ["sqlite", "sqlserver", "mariadb"],
            help="データを登録するデータベース"
        )
        
        batch_size = st.number_input(
            "バッチサイズ", 
            min_value=1, 
            max_value=1000, 
            value=100,
            help="一度に処理する件数"
        )
    
    # 登録前の最終確認
    st.subheader("📋 登録前確認")
    
    data = st.session_state.retrieved_data
    products = [Product.from_dict(item) for item in data]
    insert_service = st.session_state.insert_service
    summary = insert_service.get_insert_summary(products)
    
    # 登録予定件数の表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if insert_colors:
            st.metric("カラー登録予定", f"{summary['color_ready']:,}件")
        else:
            st.metric("カラー登録予定", "スキップ")
    
    with col2:
        if insert_sizes:
            st.metric("サイズ登録予定", f"{summary['size_ready']:,}件")
        else:
            st.metric("サイズ登録予定", "スキップ")
    
    with col3:
        total_operations = (summary['color_ready'] if insert_colors else 0) + (summary['size_ready'] if insert_sizes else 0)
        st.metric("総登録予定", f"{total_operations:,}件")
    
    # 登録対象データのプレビュー
    if st.checkbox("📊 登録対象データをプレビュー"):
        preview_data = []
        
        for product in products:
            if (insert_colors and product.color_id is not None) or (insert_sizes and product.size_id is not None):
                preview_data.append({
                    'product_id': product.product_id,
                    'product_name': product.product_name,
                    'color_name': product.color_name,
                    'color_id': product.color_id,
                    'size_name': product.size_name,
                    'size_id': product.size_id
                })
        
        if preview_data:
            preview_df = pd.DataFrame(preview_data)
            st.dataframe(preview_df, use_container_width=True, hide_index=True)
        else:
            st.info("登録対象のデータがありません")
    
    # 登録実行
    st.subheader("🚀 登録実行")
    
    if st.button("💾 データ登録を実行", type="primary", disabled=total_operations == 0):
        # 最終確認
        if not st.checkbox("⚠️ 上記の設定で登録を実行します。よろしいですか？"):
            st.warning("チェックボックスにチェックを入れてから実行してください")
            return
        
        # 登録処理の実行
        with st.spinner("データ登録を実行中..."):
            try:
                # プログレスバーの設定
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 登録処理
                status_text.text("データ検証中...")
                progress_bar.progress(10)
                
                # バッチ登録の実行
                status_text.text("データ登録中...")
                progress_bar.progress(50)
                
                batch_result = insert_service.batch_insert(
                    products, 
                    db_type, 
                    insert_colors, 
                    insert_sizes
                )
                
                progress_bar.progress(100)
                status_text.text("登録完了")
                
                # 結果の表示
                st.subheader("📊 登録結果")
                
                if batch_result['success']:
                    st.success("✅ データ登録が正常に完了しました")
                else:
                    st.error("❌ データ登録中にエラーが発生しました")
                
                # 詳細結果
                col1, col2 = st.columns(2)
                
                with col1:
                    if batch_result['color_result']:
                        color_result = batch_result['color_result']
                        st.metric(
                            "カラーデータ登録", 
                            f"{color_result['inserted_count']:,}件",
                            delta=f"スキップ: {color_result['skipped_count']:,}件"
                        )
                
                with col2:
                    if batch_result['size_result']:
                        size_result = batch_result['size_result']
                        st.metric(
                            "サイズデータ登録", 
                            f"{size_result['inserted_count']:,}件",
                            delta=f"スキップ: {size_result['skipped_count']:,}件"
                        )
                
                # エラーの表示
                if batch_result['errors']:
                    st.subheader("❌ エラー詳細")
                    for error in batch_result['errors']:
                        st.error(error)
                
                # 処理時間の表示
                if batch_result['started_at'] and batch_result['completed_at']:
                    processing_time = (batch_result['completed_at'] - batch_result['started_at']).total_seconds()
                    st.info(f"⏱️ 処理時間: {processing_time:.2f}秒")
                
                # セッション状態に保存
                st.session_state['last_insert_result'] = batch_result
                
                # 少し待ってからプログレスバーをクリア
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ データ登録エラー: {e}")
                app_logger.error(f"データ登録エラー: {e}")
    
    # 前回の登録結果の表示
    if 'last_insert_result' in st.session_state:
        st.subheader("📋 前回の登録結果")
        
        last_result = st.session_state['last_insert_result']
        
        if last_result['success']:
            st.success("✅ 前回の登録は成功しました")
        else:
            st.error("❌ 前回の登録でエラーが発生しました")
        
        # 詳細情報の表示
        with st.expander("詳細情報を表示"):
            st.json(last_result)
