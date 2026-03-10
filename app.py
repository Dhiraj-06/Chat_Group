from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
application = app
app.config['SECRET_KEY'] = 'secret!'

# Use threading instead of eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# SQLite Database Setup
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    message TEXT,
    timestamp TEXT
)
""")

conn.commit()

online_users = 0


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@socketio.on('connect')
def handle_connect():
    global online_users
    online_users += 1
    emit('user_count', online_users, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    global online_users
    online_users -= 1
    emit('user_count', online_users, broadcast=True)


@socketio.on('message')
def handle_message(data):

    username = data['username']
    message = data['message']
    timestamp = str(datetime.now())

    cursor.execute(
        "INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
        (username, message, timestamp)
    )
    conn.commit()

    send(data, broadcast=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)