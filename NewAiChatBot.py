"""
Minimal AI chatbot you can run locally.

What you get in ONE file:
- A Flask backend with a /api/chat endpoint calling OpenAI's Responses API
- Serves a tiny HTML+JS chat UI at /
- Stateless by default: the browser sends the whole chat history each turn

How to run:
1) Python 3.9+
2) pip install -r requirements (see bottom of this file)
3) Set env var:  export OPENAI_API_KEY=sk-...  (Windows: set OPENAI_API_KEY=...)
4) python app.py  → open http://127.0.0.1:5000

NOTE: Uses the OpenAI Python SDK (Responses API) and the `gpt-4o-mini` model.
"""

import os
import json
from textwrap import dedent
from flask import Flask, request, jsonify, Response
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a helpful and polite hospital helpline assistant. "
    "Your job is to answer questions about hospital services, "
    "appointments, visiting hours, and departments. "
    "If the user describes a medical emergency, immediately tell them "
    "to call 108 or visit the nearest emergency room. "
    "Always remind users that you are not a doctor and cannot give "
    "professional medical advice."
)


@app.route("/api/chat", methods=["POST"])
def chat_api():
    """Accepts JSON: {"messages": [{role, content} ...]} and returns {"reply": str}.
    The server is stateless; the client sends history each time.
    """
    try:
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        if not isinstance(messages, list):
            return jsonify({"error": "messages must be a list"}), 400

        # Prepend/ensure a system message
        history = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in messages
        ]

        # Responses API: send chat-style input; SDK merges outputs into .output_text
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=history,
        )

        reply_text = getattr(resp, "output_text", "").strip()
        if not reply_text:
            # Fallback: dig into the structure if .output_text missing for some reason
            try:
                first_item = resp.output[0]
                reply_text = first_item.content[0].text
            except Exception:
                reply_text = "(No response text received.)"

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    # A tiny chat UI with fetch(); no build tools needed.
    html = dedent(
        f"""
        <!doctype html>
        <html lang=\"en\">
        <head>
          <meta charset=\"utf-8\" />
          <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
          <title>Minimal AI Chatbot</title>
          <style>
            :root {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }}
            body {{ margin: 0; background: #0b1020; color: #e6e9f2; }}
            header {{ padding: 16px 20px; background: #0f1530; border-bottom: 1px solid #1f274a; }}
            h1 {{ margin: 0; font-size: 18px; letter-spacing: .3px; }}
            #app {{ max-width: 800px; margin: 0 auto; padding: 18px; }}
            .bubble {{ padding: 12px 14px; border-radius: 14px; margin: 10px 0; line-height: 1.5; }}
            .user {{ background: #1d2a55; align-self: flex-end; }}
            .assistant {{ background: #161d3a; }}
            .row {{ display: flex; gap: 10px; margin-top: 10px; }}
            textarea {{ flex: 1; resize: vertical; min-height: 60px; max-height: 40vh; border-radius: 12px; padding: 10px; border: 1px solid #2a376b; background: #0f1530; color: #e6e9f2; }}
            button {{ padding: 10px 14px; border-radius: 12px; border: 1px solid #2a376b; background: #1e2a58; color: #e6e9f2; cursor: pointer; }}
            button:disabled {{ opacity: .6; cursor: not-allowed; }}
            .messages {{ display: flex; flex-direction: column; }}
            .hint {{ color: #aab3d9; font-size: 13px; margin: 6px 2px 14px; }}
            .footer {{ opacity: .8; font-size: 12px; margin-top: 18px; }}
            a {{ color: #9fc3ff; }}
          </style>
        </head>
        <body>
          <header><h1>🧠 Minimal AI Chatbot</h1></header>
          <div id=\"app\">
            <div class=\"hint\">Chat is stateless; page sends full history each message. Set <code>OPENAI_API_KEY</code> in your server env.</div>
            <div id=\"messages\" class=\"messages\"></div>

            <div class=\"row\">
              <textarea id=\"input\" placeholder=\"Ask me anything...\"></textarea>
              <button id=\"send\">Send</button>
            </div>
            <div class=\"footer\">Built with Flask + OpenAI Responses API.</div>
          </div>
          <script>
            const messagesDiv = document.getElementById('messages');
            const input = document.getElementById('input');
            const sendBtn = document.getElementById('send');
            /** in-memory history the server will receive each turn */
            const history = [];

            function addBubble(role, content) {{
              const div = document.createElement('div');
              div.className = 'bubble ' + (role === 'user' ? 'user' : 'assistant');
              div.textContent = content;
              messagesDiv.appendChild(div);
              window.scrollTo(0, document.body.scrollHeight);
            }}

            async function send() {{
              const text = input.value.trim();
              if (!text) return;
              input.value = '';
              addBubble('user', text);
              history.push({{ role: 'user', content: text }});
              sendBtn.disabled = true; sendBtn.textContent = '...';
              try {{
                const res = await fetch('/api/chat', {{
                  method: 'POST',
                  headers: {{ 'Content-Type': 'application/json' }},
                  body: JSON.stringify({{ messages: history }})
                }});
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                const reply = data.reply || '(no reply)';
                addBubble('assistant', reply);
                history.push({{ role: 'assistant', content: reply }});
              }} catch (err) {{
                addBubble('assistant', '⚠️ ' + err.message);
              }} finally {{
                sendBtn.disabled = false; sendBtn.textContent = 'Send';
              }}
            }}

            sendBtn.addEventListener('click', send);
            input.addEventListener('keydown', (e) => {{
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') send();
            }});
          </script>
        </body>
        </html>
        """
    )
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    # Simple dev server
    port = int(os.getenv("PORT", 5000))
    print(f"\n➡️  Open http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)


# ------------------------------
# requirements.txt (copy these lines into a file named requirements.txt)
# ------------------------------
# Flask==3.0.3
# openai>=1.40.0


