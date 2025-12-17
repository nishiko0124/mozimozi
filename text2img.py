import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import quote

app = Flask(__name__)

# ==========================================
# 設定エリア
# ==========================================
# ここは実際に置いたフォントファイル名に合わせてね
FONT_FILENAME = "NotoSansJP-VariableFont_wght.ttf" 
IMG_SIZE = 512
FONT_SIZE = 64
TEXT_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)

def get_font():
    """フォント読み込み（パス解決付き）"""
    font_path = os.path.join(os.path.dirname(__file__), FONT_FILENAME)
    try:
        return ImageFont.truetype(font_path, FONT_SIZE)
    except IOError:
        print(f"警告: '{FONT_FILENAME}' が見つかりません。")
        return ImageFont.load_default()

@app.route('/', methods=['GET', 'POST'])
def index():
    img_url = None
    text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            # 画像URLを作成
            img_url = f'/image?text={quote(text)}'
            
    # ★変更点: templates/index.html を読み込みます
    return render_template('index.html', img_url=img_url, text=text)

@app.route('/image')
def image():
    text = request.args.get('text', 'No Text')
    
    img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    font = get_font()

    center_x = IMG_SIZE // 2
    center_y = IMG_SIZE // 2
    
    # 中央揃えで描画
    draw.text((center_x, center_y), text, fill=TEXT_COLOR, font=font, anchor="mm")

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)