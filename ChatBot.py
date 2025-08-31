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

# --- Chat UI Page ---
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏥 Hospital Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }
            #chatbox { width: 100%; max-width: 500px; margin: auto; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            #messages { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
            .user { color: blue; margin: 5px 0; }
            .bot { color: green; margin: 5px 0; }
            #inputBox { width: 80%; padding: 10px; }
            #sendBtn { padding: 10px; background: #28a745; color: white; border: none; cursor: pointer; }
            #sendBtn:hover { background: #218838; }
        </style>
    </head>
    <body>
        <div id="chatbox">
            <h2>🏥 Hospital Chatbot</h2>
            <div id="messages"></div>
            <input id="inputBox" type="text" placeholder="Type your message..." />
            <button id="sendBtn">Send</button>
        </div>

        <script>
            const inputBox = document.getElementById("inputBox");
            const sendBtn = document.getElementById("sendBtn");
            const messagesDiv = document.getElementById("messages");

            function addMessage(sender, text) {
                const msg = document.createElement("div");
                msg.className = sender;
                msg.innerText = sender.toUpperCase() + ": " + text;
                messagesDiv.appendChild(msg);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            sendBtn.addEventListener("click", async () => {
                const userText = inputBox.value.trim();
                if (!userText) return;
                addMessage("user", userText);
                inputBox.value = "";

                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ messages: [{ role: "user", content: userText }] })
                });
                const data = await response.json();
                addMessage("bot", data.reply);
            });

            inputBox.addEventListener("keypress", function(e) {
                if (e.key === "Enter") sendBtn.click();
            });
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    print("\n➡️ Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True)

