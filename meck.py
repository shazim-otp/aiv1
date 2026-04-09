import requests

# 🔑 API KEY
API_KEY = "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"

# ---------- CUSTOM RESPONSES ----------
def custom_reply(text):
    text = text.lower()

    if "who made you" in text or "who developed you" in text or "who is your developer" in text:
        return "I was developed by Shaazim."

    if "who are you" in text:
        return "I am an AI assistant powered by Nemotron."

    return None


# ---------- NEMOTRON ----------
def ask_nemotron(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [
            {
                "role": "user",
                "content": f"Answer clearly, concisely, and helpfully: {prompt}"
            }
        ],
        "temperature": 0.6,
        "max_tokens": 300
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return "AI error. Try again."

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return "AI service unavailable."


# ---------- MAIN HANDLER ----------
def handle(text):
    # 1️⃣ Check custom answers first
    custom = custom_reply(text)
    if custom:
        return custom

    # 2️⃣ Otherwise use AI
    return ask_nemotron(text)


# ---------- TEST ----------
if __name__ == "__main__":
    print("AI Ready (type 'exit')\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        reply = handle(user_input)
        print("AI:", reply)
