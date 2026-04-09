from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🔥 LIVE SEARCH FUNCTION (NEW)
def get_live_data(query):
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        res = requests.get(url).json()
        return res.get("AbstractText", "⚠️ No live data found, try rephrasing.")
    except:
        return "⚠️ Error fetching live data"

# 🔥 AI RESPONSE
def get_ai_response(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a smart AI assistant. If unsure, say you may not have latest data."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }
        )

        print("STATUS:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "⚠️ API Error: " + str(data)

    except Exception as e:
        return "Error: " + str(e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # 🔥 SMART DETECTION FOR LIVE QUESTIONS
    keywords = ["current", "latest", "now", "today", "news"]

    if any(word in user_message.lower() for word in keywords):
        live_answer = get_live_data(user_message)
        return jsonify({"response": live_answer})

    # Otherwise use AI
    reply = get_ai_response(user_message)
    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)