# 文字→画像ジェネレーター

## 概要
テキストを入力するとヒラギノ角ゴシックで正方形画像を生成するFlaskアプリです。

## 使い方
1. `requirements.txt` で依存パッケージをインストール
2. `python text2img.py` でローカル実行
3. `/` でWebフォームから文字→画像生成

## デプロイ
- Railway/Render/Heroku等で requirements.txt, Procfile, text2img.py, templates/index.html をpushすればOK

## フォントについて
- macOS標準のヒラギノ角ゴシック（/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc）を指定
- サーバーに該当フォントがない場合はデフォルトフォントで描画されます
