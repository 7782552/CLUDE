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
    
    # 2024年底仍可用的 Provider 列表（按稳定性排序）
    test_providers = [
        g4f.Provider.You,
        g4f.Provider.Liaobots,
        g4f.Provider.FreeChatgpt,
        g4f.Provider.DeepInfra,
        g4f.Provider.Replicate,
        g4f.Provider.HuggingChat,
    ]
    
    # 备选模型列表
    models_to_try = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-sonnet",
        "llama-2-70b",
    ]
    
    last_error = "Unknown error"
    
    # 先尝试不指定 Provider（让 g4f 自动选择）
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=messages,
            stream=False
        )
        if response and len(str(response)) > 5:
            return jsonify({
                "choices": [{"message": {"role": "assistant", "content": str(response)}}],
                "model": "auto-selected"
            })
    except Exception as e:
        last_error = str(e)
    
    # 然后尝试各个 Provider
    for provider in test_providers:
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                provider=provider,
                messages=messages,
                stream=False
            )
            
            if response and len(str(response)) > 5:
                return jsonify({
                    "choices": [{"message": {"role": "assistant", "content": str(response)}}],
                    "model": f"via-{provider.__name__}"
                })
        except Exception as e:
            last_error = str(e)
            continue
            
    return jsonify({"error": f"所有通道暂不可用: {last_error}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
