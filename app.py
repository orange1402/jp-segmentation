from flask import Flask, request, render_template_string
from fugashi import Tagger
from functools import lru_cache

app = Flask(__name__)

# 只有在第一次需要時才建立 Tagger，避免冷啟動逾時
@lru_cache(maxsize=1)
def get_tagger():
    return Tagger()

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
        {% for surface, feature in results %}
        <tr><td>{{ surface }}</td><td>{{ feature }}</td></tr>
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
        words = get_tagger()(text)  # 延遲初始化的 Tagger
        for word in words:
            pos1 = getattr(word.feature, "pos1", "")
            if pos_filter == "ALL" or pos1 in ["名詞", "動詞"]:
                results.append((word.surface, word.feature))
    return render_template_string(HTML_TEMPLATE, text=text, results=results, pos_filter=pos_filter)

if __name__ == "__main__":
    # 部署時不要開 debug；對外綁 0.0.0.0
    app.run(debug=False, port=5000, host="0.0.0.0")
