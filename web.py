import requests

# 🔑 API KEY
API_KEY = "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"

# ---------- CONFIG ----------
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
    "who are you": "I am an AI assistant powered by Nemotron."
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
            {
                "role": "user",
                "content": prompt.strip()
            }
        ],
        "temperature": 0.5,   # more stable
        "max_tokens": 250     # faster response
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)

        if response.status_code != 200:
            return "AI error. Please try again."

        data = response.json()

        return data.get("choices", [{}])[0].get("message", {}).get("content", "No response.")

    except requests.exceptions.Timeout:
        return "AI timeout. Try again."
    except requests.exceptions.RequestException:
        return "Network error."
    except Exception:
        return "Unexpected AI error."


# ---------- MAIN HANDLER ----------
def handle(text):
    if not text or not text.strip():
        return "Please enter a valid message."

    # 1️⃣ Custom responses
    custom = get_custom_reply(text)
    if custom:
        return custom

    # 2️⃣ AI response
    return ask_nemotron(text)


# ---------- CLI TEST ----------
if __name__ == "__main__":
    print("Nemotron AI Ready (type 'exit')\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            break

        print("AI:", handle(user_input))
