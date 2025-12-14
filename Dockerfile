# ベースとなるPython環境 (軽量版)
FROM python:3.9-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# フォルダ内の全ファイルをコンテナにコピー
COPY . .

# 必要なライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run はポート8080での通信を期待するため開放
EXPOSE 8080

# opp.py を起動するコマンド
CMD ["streamlit", "run", "opp.py", "--server.port=8080", "--server.address=0.0.0.0"]
