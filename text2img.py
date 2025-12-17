import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

app = Flask(__name__)

# フォント設定（重要：クラウドやLinux環境ではMacのフォントパスは使えません）
# 同じフォルダにフォントファイル(font.ttfなど)を置くのが一番確実です。
# ここでは一旦、エラーにならないようにデフォルトフォントへのフォールバックを強化しています。
FONT_PATH = "Hiragino Sans GB.ttc" # Mac用。Windowsなら "msgothic.ttc" など
IMG_SIZE = 512
FONT_SIZE = 64

@app.route('/', methods=['GET', 'POST'])
def index():
    img_url = None
    text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            # URLエンコードなどはブラウザが処理しますが、明示的なら urllib.parse.quote が必要
            img_url = '/image?text=' + text
    return render_template('index.html', img_url=img_url, text=text)

@app.route('/image')
def image():
    text = request.args.get('text', 'No Text')
    
    # 画像作成
    img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color='white')
    draw = ImageDraw.Draw(img)

    # フォント読み込み（失敗したらデフォルトへ）
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    # ★ここを修正しました★ (textsize -> textbbox)
    # textbbox は (left, top, right, bottom) を返します
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # 中央揃えの計算
    x = (IMG_SIZE - w) // 2
    y = (IMG_SIZE - h) // 2

    # テキスト描画（日本語を使う場合、デフォルトフォントだと文字化けします）
    # デフォルトフォントの場合、fill='black'だけだと見えないことがあるので調整
    draw.text((x, y), text, fill='black', font=font)

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) # debug=Trueにするとエラーが見やすくなります