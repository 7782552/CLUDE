import os
import g4f
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "<h1>Claude API is Online</h1><p>Status: Active</p>"

@app.route("/v1/chat/completions", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages")
    
    # 2026 年主流供应商列表，代码会自动按顺序尝试
    # 这样就算库版本稍微旧一点，没有 Nexra，它也会去试 Blackbox 或 Airforce
    test_providers = [
        "Nexra",
        "Blackbox",
        "Airforce",
        "DuckDuckGo"
    ]
    
    for p_name in test_providers:
        try:
            # 动态检查 g4f 库里是否有这个供应商
            if hasattr(g4f.Provider, p_name):
                provider = getattr(g4f.Provider, p_name)
                response = g4f.ChatCompletion.create(
                    model="claude-3-5-sonnet",
                    provider=provider,
                    messages=messages,
                    stream=False
                )
                if response and len(str(response)) > 1:
                    return jsonify({
                        "choices": [{"message": {"role": "assistant", "content": str(response)}}],
                        "model": f"claude-3.5-via-{p_name}"
                    })
        except Exception:
            continue # 如果当前供应商报错，自动尝试下一个
            
    return jsonify({"error": "All providers failed. Please try again later."}), 500

if __name__ == "__main__":
    # 适配 Render 的端口要求
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
