from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__)

# 🔑 API KEY
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

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


# ---------- AI ----------
def ask_ai(prompt):
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            stream=False   # 🔥 IMPORTANT (no streaming for web)
        )

        return completion.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", e)
        return "AI error. Try again."


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
    reply = ask_ai(message)
    return jsonify({"reply": reply})


@app.route("/health")
def health():
    return "OK"


# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
