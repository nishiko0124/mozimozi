import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import quote

app = Flask(__name__)

# ==========================================
# 設定
# ==========================================
FONT_FILENAME = "NotoSansJP-VariableFont_wght.ttf" 
IMG_WIDTH = 800     # 横幅は固定（スマホで読みやすいサイズ）
FONT_SIZE = 32      # 文字サイズも固定（小さくしない！）
LINE_HEIGHT_RATIO = 1.5 # 行間の広さ（1.5倍）
MARGIN = 40         # 余白

def get_font():
    font_path = os.path.join(os.path.dirname(__file__), FONT_FILENAME)
    try:
        return ImageFont.truetype(font_path, FONT_SIZE)
    except IOError:
        return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """横幅に合わせて改行位置を決める関数"""
    lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        # 空行の場合
        if paragraph == "":
            lines.append("")
            continue

        current_line = ""
        for char in paragraph:
            test_line = current_line + char
            # サイズ計算
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            
            if w <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        lines.append(current_line)
    return lines

@app.route('/', methods=['GET', 'POST'])
def index():
    img_url = None
    text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            img_url = f'/image?text={quote(text)}'
    return render_template('index.html', img_url=img_url, text=text)

@app.route('/image')
def image():
    text = request.args.get('text', 'No Text')
    font = get_font()

    # 1. 描画エリアの幅（横幅 - 余白）
    draw_width = IMG_WIDTH - (MARGIN * 2)

    # 2. 全行をリスト化する
    lines = wrap_text(text, font, draw_width)

    # 3. 必要な「高さ」を計算する
    # 文字1行の高さ
    bbox = font.getbbox("あ")
    text_height = bbox[3] - bbox[1]
    line_height = int(text_height * LINE_HEIGHT_RATIO)
    
    # 画像全体の高さ = (行数 × 行の高さ) + (上下の余白)
    img_height = (len(lines) * line_height) + (MARGIN * 2)

    # 4. 計算した高さでキャンバスを作る
    img = Image.new('RGB', (IMG_WIDTH, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # 5. 描画
    current_y = MARGIN
    for line in lines:
        draw.text((MARGIN, current_y), line, fill='black', font=font)
        current_y += line_height

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)