from flask import Flask, request, render_template_string
from functools import lru_cache

# 改用 SudachiPy（純 Python，不需要 MeCab）
from sudachipy import dictionary, tokenizer as sudachi_tokenizer

app = Flask(__name__)

# 首次需要時才建立 Tokenizer，避免冷啟動逾時
@lru_cache(maxsize=1)
def get_tokenizer():
    # 使用 core 詞典；mode A = 最短（細切），B/C 可較長
    t = dictionary.Dictionary().create()
    mode = sudachi_tokenizer.Tokenizer.SplitMode.A
    return t, mode

HTML_TEMPLATE = """
<!doctype html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>日文教科書文本分詞工具</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        textarea { width: 100%; height: 150px; }
        table { width: 100%; border-collapse: collapse; margin-top: 1em; }
        th, td { border: 1px solid #ccc; padding: 5px; text-align: left; }
        select { margin-top: 1em; }
        pre { background: #f9f9f9; padding: 10px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>日文教科書文本分詞工具</h1>
    <form method="post">
        <textarea name="text" placeholder="ここに日文教科書の一節を入力してください。">{{ text }}</textarea><br>
        <label for="pos_filter">品詞フィルター：</label>
        <select name="pos_filter">
            <option value="ALL" {% if pos_filter == 'ALL' %}selected{% endif %}>すべて表示</option>
            <option value="名詞動詞" {% if pos_filter == '名詞動詞' %}selected{% endif %}>名詞と動詞のみ</option>
        </select><br>
        <button type="submit">分詞実行</button>
    </form>

    {% if results %}
    <h2>分詞結果</h2>
    <table>
        <tr><th>表層</th><th>品詞</th></tr>
        {% for surface, pos in results %}
        <tr><td>{{ surface }}</td><td>{{ pos }}</td></tr>
        {% endfor %}
    </table>

    <h3>📋 表層（縦列コピー用）</h3>
    <pre>{{ results|map(attribute=0)|join('\\n') }}</pre>
    {% endif %}
</body>
</html>
"""

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    pos_filter = "ALL"
    results = []
    if request.method == "POST":
        text = request.form.get("text", "")
        pos_filter = request.form.get("pos_filter", "ALL")
        t, mode = get_tokenizer()
        morphemes = t.tokenize(text, mode)
        for m in morphemes:
            surface = m.surface()
            pos = m.part_of_speech()  # tuple，例如 ('名詞', '一般', ... )
            pos1 = pos[0] if pos else ""
            if pos_filter == "ALL" or pos1 in ["名詞", "動詞"]:
                # 這裡顯示前二層品詞，如「名詞-普通名詞」或「動詞-一般」
                pos_disp = "-".join([p for p in pos[:2] if p])
                results.append((surface, pos_disp))
    return render_template_string(HTML_TEMPLATE, text=text, results=results, pos_filter=pos_filter)

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
