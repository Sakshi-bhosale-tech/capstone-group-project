from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# --- Simple offline hospital chatbot logic ---
def hospital_bot(user_input: str) -> str:
    user_input = user_input.lower()

    if "appointment" in user_input:
        return "📅 You can book an appointment by calling our reception at +91-1234567890."
    elif "visiting hours" in user_input or "visit time" in user_input:
        return "🕙 Visiting hours are 10 AM - 1 PM and 5 PM - 7 PM daily."
    elif "emergency" in user_input or "chest pain" in user_input:
        return "⚠️ This seems urgent. Please call 108 or go to the nearest emergency room immediately."
    elif "department" in user_input or "doctor" in user_input:
        return "🏥 We have Cardiology, Neurology, Pediatrics, and General Medicine departments."
    elif "hello" in user_input or "hi" in user_input:
        return "Hello 👋 I’m your hospital assistant bot. How can I help you today?"
    else:
        return "I can help with appointments, visiting hours, departments, and emergencies."

# --- API endpoint for the chatbot ---
@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json(force=True)
    user_msg = data.get("messages", [])[-1].get("content", "")
    reply = hospital_bot(user_msg)
    return jsonify({"reply": reply})

# --- Simple homepage ---
@app.route("/")
def index():
    return Response("<h2>🏥 Hospital Chatbot is running ✅</h2><p>Send messages via /api/chat</p>", mimetype="text/html")

if __name__ == "__main__":
    print("\n➡️ Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True)


