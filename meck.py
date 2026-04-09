import json
import os
import requests
import difflib
import re

from listen import listen
from wake import WakeWord

KB_FILE = "knowledge.json"
MEM_FILE = "memory.json"

# ---------- LOAD ----------
try:
    with open(KB_FILE, "r") as f:
        KB = json.load(f)
except:
    KB = {}

try:
    with open(MEM_FILE, "r") as f:
        MEM = json.load(f)
except:
    MEM = {}

# ---------- ⚠️ API KEY (TEMP - CHANGE LATER) ----------
API_KEY = "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"

# ---------- NORMALIZE ----------
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    remove_words = [
        "meck", "please", "can you", "tell me",
        "what is", "who is", "define", "explain"
    ]
    for w in remove_words:
        text = text.replace(w, "")
    return text.strip()

# ---------- CLEAN ----------
def clean_text(text):
    return re.sub(r"[^a-z0-9\s]", "", text)

def correct_spelling(query, keys):
    words = query.split()
    corrected = []
    for w in words:
        match = difflib.get_close_matches(w, keys, n=1, cutoff=0.75)
        corrected.append(match[0] if match else w)
    return " ".join(corrected)

# ---------- WIKIPEDIA ----------
def fetch_from_wikipedia(query):
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "%20")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("extract")
    except:
        pass
    return None

def save_to_knowledge(key, value):
    KB[key] = value
    with open(KB_FILE, "w") as f:
        json.dump(KB, f, indent=2)

# ---------- 🧠 NEMOTRON ----------
def ask_nemotron(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "nvidia/nemotron-4-340b-instruct",
        "messages": [
            {"role": "user", "content": f"Answer clearly and simply: {prompt}"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        # 🔍 DEBUG (check Render logs)
        print("STATUS:", response.status_code)
        print("RAW RESPONSE:", response.text)

        if response.status_code != 200:
            return "AI error: unable to fetch response."

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        return "AI did not return a valid response."

    except Exception as e:
        print("Nemotron error:", e)
        return "AI service is not available right now."

# ---------- MATCH ----------
def keyword_score(q, k):
    return len(set(q.split()) & set(k.split()))

def find_answer(q, source):
    best_score = 0
    best_answer = None
    for k, a in source.items():
        score = keyword_score(q, k)
        if score > best_score:
            best_score = score
            best_answer = a
    return best_answer

# ---------- MEMORY ----------
def save_memory():
    with open(MEM_FILE, "w") as f:
        json.dump(MEM, f, indent=2)

def learn():
    speak("What question should I remember?")
    q = normalize(listen())

    if not q:
        speak("I did not hear the question.")
        return

    speak("What is the answer?")
    a = listen()

    if not a:
        speak("I did not hear the answer.")
        return

    MEM[q] = a
    save_memory()
    speak("Saved.")

def forget():
    speak("Which question should I forget?")
    q = normalize(listen())

    if not q:
        speak("I did not hear the question.")
        return

    if q in MEM:
        del MEM[q]
        save_memory()
        speak("Deleted.")
    else:
        speak("Memory not found.")

# ---------- SPEAK (Render safe) ----------
def speak(text):
    if not text:
        return
    print("MECK:", text)

# ---------- MAIN HANDLER ----------
def handle(text):
    text = text.lower()

    if any(q in text for q in [
        "who is your developer",
        "who developed you",
        "who made you"
    ]):
        return "I am developed by Shaazim"

    q = normalize(text)
    q = clean_text(q)

    kb_keys = list(KB.keys())
    corrected_q = correct_spelling(q, kb_keys)

    # 1️⃣ MEMORY
    if corrected_q in MEM:
        return MEM[corrected_q]

    # 2️⃣ WIKIPEDIA
    wiki_ans = fetch_from_wikipedia(corrected_q)
    if wiki_ans:
        save_to_knowledge(corrected_q, wiki_ans)
        return wiki_ans

    # 3️⃣ LOCAL KB
    ans = find_answer(corrected_q, KB)
    if ans:
        return ans

    # 4️⃣ 🔥 NEMOTRON (FINAL AI)
    return ask_nemotron(f"User asked: {corrected_q}")

# ---------- MAIN ----------
def main():
    wake = WakeWord()
    awake = False

    while True:
        try:
            if not awake:
                wake.listen()
                awake = True
                speak("Yes?")
                continue

            command = listen()
            if not command:
                continue

            if any(x in command for x in [
                "sleep",
                "go to sleep",
                "stop listening"
            ]):
                speak("Going to sleep.")
                awake = False
                continue

            response = handle(command)
            speak(response)

        except KeyboardInterrupt:
            speak("Shutting down.")
            break

        except Exception as e:
            print("Runtime error:", e)
            speak("An error occurred.")
