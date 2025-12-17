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
IMG_SIZE = 512
MAX_FONT_SIZE = 80 # 最大文字サイズ
MIN_FONT_SIZE = 10 # これ以上は小さくしない
MARGIN = 40        # 画像の端っこの余白

def get_font(size):
    """サイズを指定してフォントを読み込む"""
    font_path = os.path.join(os.path.dirname(__file__), FONT_FILENAME)
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """
    指定された幅(max_width)に収まるように、
    テキストをリスト形式の行に分割する関数
    """
    lines = []
    # ユーザーが入力した改行でまずは分割
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        current_line = ""
        for char in paragraph:
            # 今の行に1文字足して幅をチェック
            test_line = current_line + char
            bbox = font.getbbox(test_line) # (left, top, right, bottom)
            w = bbox[2] - bbox[0]
            
            if w <= max_width:
                current_line = test_line
            else:
                # 幅を超えたら今の行を確定して、次の行へ
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
    
    img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), color='white')
    draw = ImageDraw.Draw(img)

    # 描画できる最大幅と高さ（余白を引いた分）
    max_width = IMG_SIZE - (MARGIN * 2)
    max_height = IMG_SIZE - (MARGIN * 2)

    current_font_size = MAX_FONT_SIZE
    lines = []
    font = None
    line_height = 0

    # -----------------------------------------------------
    # 全文が入るサイズが見つかるまで、フォントを小さくしながらループ
    # -----------------------------------------------------
    while current_font_size >= MIN_FONT_SIZE:
        font = get_font(current_font_size)
        
        # 1. まず改行計算
        lines = wrap_text(text, font, max_width)
        
        # 2. 全体の高さを計算
        # getbbox()[3] - [1] は文字の高さ。少し行間(1.2倍)を入れる
        bbox = font.getbbox("あ") 
        text_h = bbox[3] - bbox[1]
        line_height = text_h * 1.5 # 行間を広めにとる
        
        total_text_height = line_height * len(lines)

        # 3. 枠に収まるかチェック
        if total_text_height <= max_height:
            # 収まったらループ終了
            break
        else:
            # 収まらなかったらフォントを小さくしてやり直し
            current_font_size -= 2

    # -----------------------------------------------------
    # 決定したサイズと行で描画
    # -----------------------------------------------------
    # 全体の高さから書き出しのY座標（上端）を計算して、垂直方向も中央揃えにする
    total_height = line_height * len(lines)
    current_y = (IMG_SIZE - total_height) // 2
    
    # 1行ずつ描画
    for line in lines:
        # 行ごとの幅を計算して、水平方向の中央揃え
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        x = (IMG_SIZE - w) // 2
        
        # 文字を書く（少し微調整しています）
        draw.text((x, current_y), line, fill='black', font=font)
        current_y += line_height

    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)