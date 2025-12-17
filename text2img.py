import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

app = Flask(__name__)

# ヒラギノ角ゴシックのパス例（macOS標準）
FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc"
IMG_SIZE = 512  # 正方形サイズ
FONT_SIZE = 64  # 適宜調整

@app.route('/', methods=['GET', 'POST'])
def index():
    img_url = None
    text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            img_url = '/image?text=' + text
    return render_template('index.html', img_url=img_url, text=text)

@app.route('/image')
def image():
    text = request.args.get('text', '')
    img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color='white')
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(text, font=font)
    x = (IMG_SIZE - w) // 2
    y = (IMG_SIZE - h) // 2
    draw.text((x, y), text, fill='black', font=font)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
