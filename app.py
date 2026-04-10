from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

BING_API_KEY = os.getenv("BING_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 📰 NEWS (Bing)
def get_news(query):
    try:
        url = "https://api.bing.microsoft.com/v7.0/news/search"
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": query, "count": 1, "mkt": "en-IN"}

        res = requests.get(url, headers=headers, params=params).json()

        if "value" in res and len(res["value"]) > 0:
            article = res["value"][0]
            return f"{article['name']} — {article['description']} (Source: {article['provider'][0]['name']})"
        else:
            return None
    except:
        return None

# 🌐 FACTUAL LIVE DATA (Wikipedia)
def get_fact(query):
    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": os.getenv("BING_API_KEY")}
        params = {"q": query, "count": 1, "mkt": "en-IN"}

        res = requests.get(url, headers=headers, params=params).json()

        if "webPages" in res and len(res["webPages"]["value"]) > 0:
            result = res["webPages"]["value"][0]
            return f"{result['name']} — {result['snippet']}"
        else:
            return None
    except Exception as e:
        return None
    except:
        return None
# 🤖 AI fallback
def get_ai_response(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a smart AI assistant. Always give the latest correct answer. Do not mention knowledge cutoff."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
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
    msg = user_message.lower()

    # 🔥 NEWS
    if any(word in msg for word in ["news", "latest", "breaking"]):
        news = get_live_data(user_message)
        if news:
            return jsonify({"response": news})

    # 🔥 FACT (VERY IMPORTANT)
    if any(word in msg for word in ["who is", "current", "present", "cm", "minister"]):
        fact = get_fact(user_message)
        if fact:
            return jsonify({"response": fact})

    # 🤖 fallback AI
    reply = get_ai_response(user_message)
    return jsonify({"response": reply})
    # 🤖 fallback
    reply = get_ai_response(user_message)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
