# カラーサイズメンテナンスツール

## 概要

商品データのカラー名とサイズ名をIDに変換するためのメンテナンスツールです。

## 機能

- 📊 データ取得機能
- 🔄 変換処理機能
- 📋 変換表管理機能
- 💾 データ登録機能

## 技術スタック

- **フレームワーク**: Streamlit
- **言語**: Python 3.11+
- **データベース**: SQL Server, MariaDB, SQLite
- **ORM**: SQLAlchemy

## セットアップ

### 1. 環境構築

```bash
# プロジェクトディレクトリに移動
cd color_size_tool

# 仮想環境を作成
python -m venv venv

# 仮想環境をアクティベート
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. 環境変数設定

```bash
# 環境変数ファイルをコピー
copy env.example .env

# .envファイルを編集してデータベース接続情報を設定
```

### 3. アプリケーション起動

```bash
# Streamlitアプリケーションを起動
streamlit run main.py
```

## 使用方法

1. **データ取得**: 商品データをデータベースから取得
2. **変換処理**: カラー名・サイズ名をIDに変換
3. **変換表管理**: 変換ルールを管理
4. **データ登録**: 変換結果をデータベースに登録

## プロジェクト構成

```
color_size_tool/
├── main.py                    # メインアプリケーション
├── requirements.txt           # 依存関係
├── config/                    # 設定ファイル
├── models/                    # データモデル
├── services/                  # ビジネスロジック
├── pages/                     # Streamlitページ
├── utils/                     # ユーティリティ
├── data/                      # データファイル
├── logs/                      # ログファイル
└── docs/                      # ドキュメント
```

## ライセンス

このプロジェクトは内部使用のためのツールです。
