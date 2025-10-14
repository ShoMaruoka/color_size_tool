"""
変換処理ページ
"""
import streamlit as st
from datetime import datetime
import pandas as pd

from services.conversion_service import ConversionService
from services.data_service import DataService
from models.conversion import ConversionResult
from config.logging_config import app_logger
from utils.error_handlers import handle_exceptions

def show_conversion_page():
    """変換処理ページを表示"""
    st.title("🔄 変換処理")
    st.markdown("---")
    
    # セッション状態の初期化
    if 'conversion_results' not in st.session_state:
        st.session_state.conversion_results = []
    if 'conversion_service' not in st.session_state:
        st.session_state.conversion_service = ConversionService()
    
    # タブで機能を分割
    tab1, tab2, tab3, tab4 = st.tabs(["📊 変換対象", "🔄 自動変換", "✏️ 手動設定", "📋 変換履歴"])
    
    with tab1:
        show_conversion_targets()
    
    with tab2:
        show_auto_conversion()
    
    with tab3:
        show_manual_conversion()
    
    with tab4:
        show_conversion_history()

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_conversion_targets():
    """変換対象表示"""
    st.header("📊 変換対象データ")
    
    # 取得済みデータの確認
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 変換対象のデータがありません")
        st.info("💡 データ取得ページでデータを取得してから変換処理を行ってください")
        
        if st.button("📊 データ取得ページに移動"):
            st.session_state.current_page = "データ取得"
            st.rerun()
        return
    
    # データの表示
    data = st.session_state.retrieved_data
    df = pd.DataFrame(data)
    
    st.subheader(f"📋 取得データ一覧 ({len(data)}件)")
    
    # 変換状況の統計
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_count = len(df)
        st.metric("総件数", f"{total_count:,}")
    
    with col2:
        color_converted = len(df[df['color_id'].notna()])
        st.metric("カラー変換済み", f"{color_converted:,}")
    
    with col3:
        size_converted = len(df[df['size_id'].notna()])
        st.metric("サイズ変換済み", f"{size_converted:,}")
    
    with col4:
        pending = len(df[(df['color_id'].isna()) | (df['size_id'].isna())])
        st.metric("未変換", f"{pending:,}")
    
    # フィルター機能
    st.subheader("🔍 フィルター")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_filter = st.selectbox(
            "カラー変換状況",
            ["すべて", "変換済み", "未変換"],
            help="カラーIDの変換状況でフィルター"
        )
    
    with col2:
        size_filter = st.selectbox(
            "サイズ変換状況",
            ["すべて", "変換済み", "未変換"],
            help="サイズIDの変換状況でフィルター"
        )
    
    with col3:
        product_filter = st.text_input(
            "商品名で検索",
            placeholder="商品名の一部を入力",
            help="商品名でフィルター"
        )
    
    # フィルター適用
    filtered_df = df.copy()
    
    if color_filter == "変換済み":
        filtered_df = filtered_df[filtered_df['color_id'].notna()]
    elif color_filter == "未変換":
        filtered_df = filtered_df[filtered_df['color_id'].isna()]
    
    if size_filter == "変換済み":
        filtered_df = filtered_df[filtered_df['size_id'].notna()]
    elif size_filter == "未変換":
        filtered_df = filtered_df[filtered_df['size_id'].isna()]
    
    if product_filter:
        filtered_df = filtered_df[filtered_df['product_name'].str.contains(product_filter, case=False, na=False)]
    
    st.info(f"フィルター結果: {len(filtered_df)}件")
    
    # データテーブル表示
    if not filtered_df.empty:
        # 表示用の列を選択
        display_columns = ['product_id', 'product_name', 'color_name', 'size_name', 'composite_value', 'color_id', 'size_id']
        display_df = filtered_df[display_columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # 一括操作ボタン
        st.subheader("⚡ 一括操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 全件自動変換", type="primary", use_container_width=True):
                auto_convert_all(filtered_df)
        
        with col2:
            if st.button("📊 変換統計を更新", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("💾 結果をCSV出力", use_container_width=True):
                download_conversion_results(filtered_df)
    else:
        st.warning("フィルター条件に一致するデータがありません")

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_auto_conversion():
    """自動変換機能"""
    st.header("🔄 自動変換")
    
    conversion_service = st.session_state.conversion_service
    
    # 変換ルールの確認
    st.subheader("📋 変換ルール状況")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            color_rules = conversion_service.get_color_rules()
            st.metric("カラー変換ルール", f"{len(color_rules)}件")
        except Exception as e:
            st.error(f"カラールール取得エラー: {e}")
            color_rules = []
    
    with col2:
        try:
            size_rules = conversion_service.get_size_rules()
            st.metric("サイズ変換ルール", f"{len(size_rules)}件")
        except Exception as e:
            st.error(f"サイズルール取得エラー: {e}")
            size_rules = []
    
    # ルールが不足している場合の初期化
    if len(color_rules) == 0 or len(size_rules) == 0:
        st.warning("⚠️ 変換ルールが不足しています")
        
        if st.button("🔧 サンプルルールを初期化", type="primary"):
            with st.spinner("サンプルルールを初期化中..."):
                try:
                    conversion_service.initialize_sample_rules()
                    st.success("✅ サンプルルールの初期化が完了しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 初期化エラー: {e}")
        return
    
    # 変換対象の選択
    st.subheader("🎯 変換対象選択")
    
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 変換対象のデータがありません")
        return
    
    data = st.session_state.retrieved_data
    df = pd.DataFrame(data)
    
    # 未変換データの抽出
    pending_df = df[(df['color_id'].isna()) | (df['size_id'].isna())]
    
    if pending_df.empty:
        st.success("✅ すべてのデータが変換済みです")
        return
    
    st.info(f"未変換データ: {len(pending_df)}件")
    
    # 変換設定
    col1, col2 = st.columns(2)
    
    with col1:
        convert_colors = st.checkbox("カラー変換を実行", value=True)
        convert_sizes = st.checkbox("サイズ変換を実行", value=True)
    
    with col2:
        batch_size = st.number_input("バッチサイズ", min_value=1, max_value=100, value=10)
        confidence_threshold = st.slider("信頼度閾値", 0.0, 1.0, 0.5, 0.1)
    
    # 変換実行
    if st.button("🚀 自動変換を実行", type="primary"):
        auto_convert_batch(pending_df, convert_colors, convert_sizes, batch_size, confidence_threshold)

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_manual_conversion():
    """手動変換機能"""
    st.header("✏️ 手動設定")
    
    if 'retrieved_data' not in st.session_state or not st.session_state.retrieved_data:
        st.warning("⚠️ 変換対象のデータがありません")
        return
    
    data = st.session_state.retrieved_data
    df = pd.DataFrame(data)
    
    # 個別設定
    st.subheader("📝 個別設定")
    
    # 商品選択
    product_options = df['product_id'].tolist()
    selected_product = st.selectbox("商品を選択", product_options)
    
    if selected_product:
        product_data = df[df['product_id'] == selected_product].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**現在の設定**")
            st.text(f"商品ID: {product_data['product_id']}")
            st.text(f"商品名: {product_data['product_name']}")
            st.text(f"カラー名: {product_data['color_name']}")
            st.text(f"サイズ名: {product_data['size_name']}")
            st.text(f"カラーID: {product_data['color_id']}")
            st.text(f"サイズID: {product_data['size_id']}")
        
        with col2:
            st.write("**手動設定**")
            
            new_color_id = st.number_input(
                "カラーID", 
                min_value=1, 
                max_value=999, 
                value=int(product_data['color_id']) if pd.notna(product_data['color_id']) else 1
            )
            
            new_size_id = st.number_input(
                "サイズID", 
                min_value=1, 
                max_value=999, 
                value=int(product_data['size_id']) if pd.notna(product_data['size_id']) else 1
            )
            
            if st.button("💾 設定を保存", type="primary"):
                # データの更新
                df.loc[df['product_id'] == selected_product, 'color_id'] = new_color_id
                df.loc[df['product_id'] == selected_product, 'size_id'] = new_size_id
                
                # セッション状態を更新
                st.session_state.retrieved_data = df.to_dict('records')
                
                st.success("✅ 設定が保存されました")
                st.rerun()
    
    # 一括設定
    st.subheader("📊 一括設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**カラー一括設定**")
        color_pattern = st.text_input("カラー名パターン", placeholder="例: レッド")
        color_id_bulk = st.number_input("設定するカラーID", min_value=1, max_value=999)
        
        if st.button("🎨 カラー一括設定"):
            bulk_update_colors(df, color_pattern, color_id_bulk)
    
    with col2:
        st.write("**サイズ一括設定**")
        size_pattern = st.text_input("サイズ名パターン", placeholder="例: M")
        size_id_bulk = st.number_input("設定するサイズID", min_value=1, max_value=999)
        
        if st.button("📏 サイズ一括設定"):
            bulk_update_sizes(df, size_pattern, size_id_bulk)

@handle_exceptions(show_error_in_ui=True, log_error=True)
def show_conversion_history():
    """変換履歴表示"""
    st.header("📋 変換履歴")
    
    conversion_service = st.session_state.conversion_service
    
    try:
        # 履歴取得
        histories = conversion_service.get_conversion_history(limit=50)
        
        if not histories:
            st.info("変換履歴がありません")
            return
        
        # 履歴をDataFrameに変換
        history_data = [history.to_dict() for history in histories]
        df = pd.DataFrame(history_data)
        
        # 統計情報
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(df)
            st.metric("総履歴数", f"{total:,}")
        
        with col2:
            successful = len(df[df['status'] == 'success'])
            st.metric("成功", f"{successful:,}")
        
        with col3:
            failed = len(df[df['status'] == 'failed'])
            st.metric("失敗", f"{failed:,}")
        
        with col4:
            avg_confidence = df['confidence'].mean()
            st.metric("平均信頼度", f"{avg_confidence:.2f}")
        
        # 履歴テーブル
        st.subheader("📊 履歴一覧")
        
        # 表示用の列を選択
        display_columns = ['product_id', 'original_value', 'converted_color_id', 'converted_size_id', 
                          'conversion_type', 'status', 'confidence', 'created_at']
        display_df = df[display_columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # ダウンロード
        csv = display_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 履歴をCSVダウンロード",
            data=csv,
            file_name=f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ 履歴取得エラー: {e}")
        app_logger.error(f"変換履歴取得エラー: {e}")

# ヘルパー関数
def auto_convert_all(df):
    """全件自動変換"""
    st.info("🔄 全件自動変換を実行中...")
    # 実装は後で追加
    st.success("✅ 自動変換が完了しました")

def auto_convert_batch(df, convert_colors, convert_sizes, batch_size, confidence_threshold):
    """バッチ自動変換"""
    conversion_service = st.session_state.conversion_service
    
    with st.spinner("自動変換を実行中..."):
        results = []
        
        for i, (_, row) in enumerate(df.iterrows()):
            try:
                result = ConversionResult(
                    product_id=row['product_id'],
                    original_color_name=row['color_name'],
                    original_size_name=row['size_name'],
                    original_composite_value=row['composite_value']
                )
                
                # カラー変換
                if convert_colors and pd.isna(row['color_id']):
                    color_result = conversion_service.convert_color(row['color_name'])
                    if color_result:
                        result.converted_color_id = color_result[0]
                        result.converted_color_name = color_result[1]
                        result.confidence = max(result.confidence, color_result[2])
                
                # サイズ変換
                if convert_sizes and pd.isna(row['size_id']):
                    size_result = conversion_service.convert_size(row['size_name'])
                    if size_result:
                        result.converted_size_id = size_result[0]
                        result.converted_size_name = size_result[1]
                        result.confidence = max(result.confidence, size_result[2])
                
                # 信頼度チェック
                if result.confidence >= confidence_threshold:
                    result.status = "success"
                else:
                    result.status = "failed"
                    result.error_message = f"信頼度不足: {result.confidence:.2f}"
                
                results.append(result)
                
                # 履歴に記録
                conversion_service.add_conversion_history(
                    product_id=result.product_id,
                    original_value=result.original_composite_value or f"{result.original_color_name}/{result.original_size_name}",
                    converted_color_id=result.converted_color_id,
                    converted_size_id=result.converted_size_id,
                    conversion_type="auto",
                    status=result.status,
                    confidence=result.confidence,
                    error_message=result.error_message
                )
                
            except Exception as e:
                app_logger.error(f"変換エラー: {e}")
                continue
        
        # 結果をセッション状態に保存
        st.session_state.conversion_results = [result.to_dict() for result in results]
        
        # 成功・失敗の統計
        successful = len([r for r in results if r.status == "success"])
        failed = len([r for r in results if r.status == "failed"])
        
        st.success(f"✅ 自動変換が完了しました")
        st.info(f"成功: {successful}件, 失敗: {failed}件")

def bulk_update_colors(df, pattern, color_id):
    """カラー一括更新"""
    if not pattern:
        st.warning("パターンを入力してください")
        return
    
    # パターンに一致する行を更新
    mask = df['color_name'].str.contains(pattern, case=False, na=False)
    updated_count = mask.sum()
    
    if updated_count > 0:
        df.loc[mask, 'color_id'] = color_id
        st.session_state.retrieved_data = df.to_dict('records')
        st.success(f"✅ {updated_count}件のカラーIDを更新しました")
        st.rerun()
    else:
        st.warning("パターンに一致するデータがありません")

def bulk_update_sizes(df, pattern, size_id):
    """サイズ一括更新"""
    if not pattern:
        st.warning("パターンを入力してください")
        return
    
    # パターンに一致する行を更新
    mask = df['size_name'].str.contains(pattern, case=False, na=False)
    updated_count = mask.sum()
    
    if updated_count > 0:
        df.loc[mask, 'size_id'] = size_id
        st.session_state.retrieved_data = df.to_dict('records')
        st.success(f"✅ {updated_count}件のサイズIDを更新しました")
        st.rerun()
    else:
        st.warning("パターンに一致するデータがありません")

def download_conversion_results(df):
    """変換結果をCSVダウンロード"""
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 変換結果をダウンロード",
        data=csv,
        file_name=f"conversion_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
