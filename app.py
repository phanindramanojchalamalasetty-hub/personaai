from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# 👉 PASTE YOUR OPENROUTER API KEY HERE
API_KEY = "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"

def get_ai_response(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            }
        )

        # Debug (optional)
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
    reply = get_ai_response(user_message)
    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)