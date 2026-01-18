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
    
    # 定义多个备选供应商，防止其中一个找不到或报错
    provider_list = [
        "Airforce", 
        "Blackbox", 
        "DuckDuckGo"
    ]
    
    for p_name in provider_list:
        try:
            # 动态获取供应商对象，防止版本不支持导致崩溃
            provider_obj = getattr(g4f.Provider, p_name)
            response = g4f.ChatCompletion.create(
                model="claude-3-5-sonnet", # 或者用 gpt-4o
                provider=provider_obj,
                messages=messages,
                stream=False
            )
            if response and len(str(response)) > 5:
                return jsonify({"choices": [{"message": {"role": "assistant", "content": str(response)}}], "model": p_name})
        except Exception as e:
            print(f"尝试 {p_name} 失败: {str(e)}")
            continue

    return jsonify({"error": "当前所有供应商均不可用，请稍后重试"}), 500
