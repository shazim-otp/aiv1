from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔑 API KEY
API_KEY = "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"

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ---------- CUSTOM RESPONSES ----------
CUSTOM_RESPONSES = {
    "who made you": "I was developed by Shaazim.",
    "who developed you": "I was developed by Shaazim.",
    "who is your developer": "I was developed by Shaazim.",
    "who are you": "I am an AI assistant powered by mecknown."
}

def get_custom_reply(text):
    text = text.lower()
    for key, value in CUSTOM_RESPONSES.items():
        if key in text:
            return value
    return None

# ---------- AI ----------
def ask_nemotron(prompt):
    payload = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 250
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)

        if response.status_code != 200:
            return "AI error"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except:
        return "AI unavailable"

# ---------- ROUTES ----------
@app.route("/")
def home():
    return "Nemotron AI is running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    if not message:
        return jsonify({"reply": "Empty message"})

    # custom first
    custom = get_custom_reply(message)
    if custom:
        return jsonify({"reply": custom})

    # AI
    reply = ask_nemotron(message)
    return jsonify({"reply": reply})

# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
