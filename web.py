from flask import Flask, request, jsonify, send_from_directory
from meck import handle
import json
from datetime import datetime
import os

app = Flask(__name__)

USERS_FILE = "users.json"
LOGS_FILE = "logs.json"

# ---------- SAFE LOAD ----------
def load_users():
    try:
        with open(USERS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_logs():
    try:
        with open(LOGS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_logs(data):
    with open(LOGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------- BASIC ROUTES ----------
@app.route("/")
def index():
    return send_from_directory(".", "web.html")

@app.route("/health")
def health():
    return "OK"

# ---------- USER ----------
@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username", "").strip()

    if not username:
        return jsonify({"status": "error"})

    users = load_users()

    if username not in users:
        users[username] = {
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users)

    return jsonify({"status": "ok"})

# ---------- CHAT ----------
@app.route("/command", methods=["POST"])
def command():
    try:
        data = request.json
        text = data.get("text", "")
        username = data.get("username", "unknown")

        reply = handle(text)  # ✅ fixed

        logs = load_logs()
        logs.append({
            "user": username,
            "question": text,
            "reply": reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_logs(logs)

        return jsonify({"reply": reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Server error occurred"})

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    users = load_users()
    logs = load_logs()

    return jsonify({
        "users": users,
        "logs": logs
    })

@app.route("/admin-data")
def admin_data():
    users = load_users()
    logs = load_logs()

    return jsonify({
        "total_users": len(users),
        "total_logs": len(logs),
        "users": users,
        "logs": logs
    })

# ---------- KNOWLEDGE ----------
@app.route("/knowledge")
def view_knowledge():
    try:
        with open("knowledge.json") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

# ---------- KNOWLEDGE UI ----------
@app.route("/knowledge-ui")
def knowledge_ui():
    return send_from_directory(".", "knowledge_admin.html")

@app.route("/knowledge-data")
def knowledge_data():
    try:
        with open("knowledge.json") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({})

# ---------- ADD ----------
@app.route("/knowledge-add", methods=["POST"])
def knowledge_add():
    data = request.json
    question = data.get("question", "").strip().lower()
    answer = data.get("answer", "").strip()

    if not question or not answer:
        return jsonify({"status": "error"})

    try:
        with open("knowledge.json") as f:
            kb = json.load(f)
    except:
        kb = {}

    kb[question] = answer

    with open("knowledge.json", "w") as f:
        json.dump(kb, f, indent=2)

    return jsonify({"status": "ok"})

# ---------- DELETE ----------
@app.route("/knowledge-delete", methods=["POST"])
def knowledge_delete():
    question = request.json.get("question", "").strip().lower()

    try:
        with open("knowledge.json") as f:
            kb = json.load(f)
    except:
        kb = {}

    if question in kb:
        del kb[question]
        with open("knowledge.json", "w") as f:
            json.dump(kb, f, indent=2)
        return jsonify({"status": "deleted"})

    return jsonify({"status": "not_found"})

# ---------- UPLOAD (MERGE) ----------
@app.route("/knowledge-upload", methods=["POST"])
def knowledge_upload():
    if "file" not in request.files:
        return jsonify({"status": "no_file"})

    file = request.files["file"]

    if not file.filename.endswith(".json"):
        return jsonify({"status": "invalid_file"})

    try:
        uploaded = json.load(file)
        if not isinstance(uploaded, dict):
            return jsonify({"status": "invalid_json"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

    try:
        with open("knowledge.json") as f:
            kb = json.load(f)
    except:
        kb = {}

    kb.update(uploaded)

    with open("knowledge.json", "w") as f:
        json.dump(kb, f, indent=2)

    return jsonify({
        "status": "ok",
        "added": len(uploaded)
    })

# ---------- START ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
