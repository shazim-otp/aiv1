from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

# 🔑 API KEY (replace this)
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
    "who are you": "I am an AI assistant powered by Mecknown."
}

def get_custom_reply(text):
    text = text.lower()
    for key, value in CUSTOM_RESPONSES.items():
        if key in text:
            return value
    return None


# ---------- NEMOTRON ----------
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

        print("STATUS:", response.status_code)
        print("RAW:", response.text)

        if response.status_code != 200:
            return "AI error. Try again."

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "No response.")

    except requests.exceptions.Timeout:
        return "AI timeout. Try again."
    except requests.exceptions.RequestException:
        return "Network error."
    except Exception as e:
        print("ERROR:", e)
        return "Unexpected error."


# ---------- ROUTES ----------
@app.route("/")
def index():
    return send_from_directory(".", "web.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please enter a message."})

    # 1️⃣ Custom replies
    custom = get_custom_reply(message)
    if custom:
        return jsonify({"reply": custom})

    # 2️⃣ AI response
    reply = ask_nemotron(message)
    return jsonify({"reply": reply})


@app.route("/health")
def health():
    return "OK"


# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
