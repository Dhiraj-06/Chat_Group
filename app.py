from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# MongoDB
client = MongoClient("mongodb+srv://scremer61_db_user:CzNnzUb1n7lwNGRT@chatgroup.fehvgxy.mongodb.net/?appName=ChatGroup")
db = client["chatdb"]
messages_collection = db["messages"]

# 🔥 Online Users Counter
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
    message_data = {
        "username": data['username'],
        "message": data['message'],
        "timestamp": datetime.now()
    }
    messages_collection.insert_one(message_data)
    send(data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)