import os
import g4f
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages")
    
    # 2026年 Railway 环境下实测最稳供应商
    try:
        # 尝试 Nexra 提供的 Claude 3.5
        from g4f.Provider import Nexra
        response = g4f.ChatCompletion.create(
            model="claude-3-5-sonnet",
            provider=Nexra,
            messages=messages
        )
        if response:
            return jsonify({"choices": [{"message": {"role": "assistant", "content": str(response)}}]})
    except Exception as e:
        # 如果失败，自动保底到 GPT-4o
        try:
            res = g4f.ChatCompletion.create(model="gpt-4o", messages=messages)
            return jsonify({"choices": [{"message": {"role": "assistant", "content": f"(Claude拥挤，切换至GPT-4o): {str(res)}"}}]})
        except:
            return jsonify({"error": "Service Unavailable"}), 503

if __name__ == "__main__":
    # Railway 必须读取环境变量中的 PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
