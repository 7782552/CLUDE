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
    
    # 筛选出 2026 年目前对云服务器 IP 最宽容的供应商
    test_providers = [
        g4f.Provider.Airforce, # 第一优先级：目前云端最稳
        g4f.Provider.Blackbox, # 第二优先级：备用
        g4f.Provider.DarkAI    # 第三优先级：保底
    ]
    
    last_error = "Unknown error"
    
    for provider in test_providers:
        try:
            # 使用更强劲的请求模式
            response = g4f.ChatCompletion.create(
                model="claude-3-5-sonnet",
                provider=provider,
                messages=messages,
                auth=True, # 尝试开启模拟授权
                stream=False
            )
            
            if response and len(str(response)) > 5:
                return jsonify({
                    "choices": [{"message": {"role": "assistant", "content": str(response)}}],
                    "model": f"claude-3.5-via-{provider.__name__}"
                })
        except Exception as e:
            last_error = str(e)
            continue
            
    return jsonify({"error": f"所有通道暂不可用。最后一次尝试报错: {last_error}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
