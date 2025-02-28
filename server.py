from flask import Flask, request, jsonify, render_template
from ollama import chat

app = Flask(__name__)

# Global dictionary for session-based conversations.
# In production, use a database or more robust storage.
user_sessions = {}

@app.route('/')
def index():
    # Render index.html from the templates folder
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_route():
    """
    Expects JSON of the form:
    {
      "session_id": "someUniqueId",
      "user_input": "Hello!"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data recieved"}), 400
    
    session_id = data.get('session_id', 'default_session')
    user_input = data.get('user_input', '')

    # Retrieve or initialize messages for this session
    messages = user_sessions.get(session_id, [])

    # Add the user's message
    messages.append({'role': 'user', 'content': user_input})

    # Generate response
    assistant_reply = ''
    for part in chat('llamaQuiz', messages=messages, stream=True):
        assistant_reply += part['message']['content']
    
    # Add assistant's response to the conversation
    messages.append({'role': 'assistant', 'content': assistant_reply})

    # Update the conversation in the in-memory sessions
    user_sessions[session_id] = messages

    # Return the assistant's reply (and optionally the entire conversation)
    return jsonify({
        'assistant_reply': assistant_reply,
        'messages': messages,
        'session_id': session_id
    })

if __name__ == "__main__":
    # Run the development server
    app.run(debug=True)
