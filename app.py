from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# 🔑 Store your Bing News API key in environment variable
BING_API_KEY = os.getenv("BING_API_KEY")

# ✅ Function to get live news
def get_live_data(query):
    try:
        url = "https://api.bing.microsoft.com/v7.0/news/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": query, "count": 1, "mkt": "en-IN"}  # India market
        res = requests.get(url, headers=headers, params=params).json()

        if "value" in res and len(res["value"]) > 0:
            article = res["value"][0]
            return f"{article['name']} — {article['description']} (Source: {article['provider'][0]['name']})"
        else:
            return "⚠️ No live news found, try rephrasing."
    except Exception as e:
        return f"⚠️ Error fetching live data: {str(e)}"

# 🔥 AI fallback response
def get_ai_response(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a smart AI assistant."},
                    {"role": "user", "content": user_input}
                ]
            }
        )
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

    keywords = ["current", "latest", "now", "today", "news"]

    # ✅ Try live data first if keyword matches
    if any(word in user_message.lower() for word in keywords):
        live_answer = get_live_data(user_message)
        if "⚠️" not in live_answer:
            return jsonify({"response": live_answer})

    # 🔥 Fallback to AI
    reply = get_ai_response(user_message)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

