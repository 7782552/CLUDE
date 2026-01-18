import os
import g4f
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 加上这个，你用浏览器直接打开链接就不会报 404 了
@app.route("/")
def index():
    return "<h1>API 运行中</h1><p>请使用 POST 请求访问 /v1/chat/completions</p>"

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json
    try:
        # 强制指定目前最稳的 Claude 供应商
        response = g4f.ChatCompletion.create(
            model="claude-3-5-sonnet",
            provider=g4f.Provider.Nexra,
            messages=data.get("messages"),
            stream=False
        )
        return jsonify({"choices": [{"message": {"role": "assistant", "content": str(response)}}]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render 必须监听 10000 端口
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
