import time
import random
import string
from flask import Flask, request, jsonify
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        message_type TEXT NOT NULL,
        message TEXT NOT NULL
    )
''')

conn.close()

app = Flask(__name__)


@app.route("/")
def get_logs():
    log_conn = sqlite3.connect("database.db")
    log_cursor = log_conn.cursor()
    res = log_cursor.execute("select timestamp, message_type, message from logs")
    logs_from_db = res.fetchall()
    log_conn.close()

    html = ""
    for log_item in logs_from_db:
        log_entry = " | ".join(map(str, log_item))
        html += f"<p>{log_entry}</p>"

    return html


@app.route("/create_log_bucket", methods=['POST'])
def create_log_bucket():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    try:
        with open(f"{random_string}.db") as file:
            file.write('')
    except FileExistsError:
        print("file already exists")

    return jsonify({'token': random_string})


@app.route("/log", methods=['POST'])
def log():
    data = request.json

    if 'message' not in data:
        return jsonify({'error': 'Missing message'}), 400

    message = data['message']
    message_type = data.get('message_type', 'info')  # Default to 'info' if not provided

    if message_type not in ['info', 'error']:
        return jsonify({'error': 'Invalid message_type value'}), 400

    # Process the message here as needed
    insert_log(message, message_type)

    return jsonify({'message_received': message, 'message_type_received': message_type}), 200


def insert_log(message, message_type):
    log_conn = sqlite3.connect("database.db")
    log_cursor = log_conn.cursor()
    timestamp = int(time.time())
    log_cursor.execute("INSERT INTO logs (timestamp, message_type, message) VALUES (?, ?, ?)",
                       (timestamp, message_type, message))
    log_conn.commit()
    log_conn.close()
