# chord-analysis バックエンド

## 必要なもの

```
Docker:
https://docs.docker.jp/get-docker.html

google cloud sdk:
https://cloud.google.com/sdk/docs/install?hl=JA

```

## GCP 関連

※ノーヴァのメンバーで権限がない場合は sysdev チームの誰かに言ってください

```
// ログイン
gcloud auth login

// gcloud sdk 初期化
// プロジェクトを選択
// regionは設定しないか、asia-northeast1でok
gcloud init

// すでにgcloud sdkのコンフィグがある場合以下でプロジェクト切り替え
gcloud config set project midi-converter-314311

```

### シークレット 取得

```
make get-sa
```

## API 起動（ローカル）

```
docker-compose up
docker exec -it ca sh
# python main.py
```

volumes でローカルと docker でファイルを共有しているため、  
コードの修正しても docker 内で `python main.py` をもう一度実行すれば ok

## デプロイ

main ブランチにマージされたら自動でデプロイ
