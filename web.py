from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔑 API KEY (REPLACE THIS)

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
messages=[{"role": "user", "content": prompt}],
temperature=0.7,
max_tokens=500,
stream=False
)
return completion.choices[0].message.content

```
except Exception as e:
    print("AI ERROR:", e)
    return "AI service unavailable."
```

# ---------- ROUTES ----------

@app.route("/chat", methods=["POST"])
def chat():
data = request.json
message = data.get("message", "").strip()

```
if not message:
    return jsonify({"reply": "Please enter a message."})

custom = get_custom_reply(message)
if custom:
    return jsonify({"reply": custom})

reply = ask_ai(message)
return jsonify({"reply": reply})
```

@app.route("/health")
def health():
return "OK"

if **name** == "**main**":
app.run(host="0.0.0.0", port=10000)
