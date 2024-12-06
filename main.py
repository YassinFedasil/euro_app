from flask import Flask, render_template_string
from flask_socketio import SocketIO
import time
import threading
import os
app = Flask(__name__)
socketio = SocketIO(app)

counter = 0

def counter_loop():
    global counter
    while True:
        time.sleep(5)
        counter += 1
        socketio.emit('update_counter', {'counter': counter})  # Envoie la mise à jour du compteur aux clients connectés

@app.route("/")
def home():
    return render_template_string("""
        <html>
            <head>
                <title>Counter</title>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
                <script type="text/javascript">
                    // Connexion au serveur WebSocket
                    var socket = io.connect('http://127.0.0.1:5000');
                    socket.on('update_counter', function(data) {
                        document.getElementById('counter').innerText = "Counter is at: " + data.counter;
                    });
                </script>
            </head>
            <body>
                <h1 id="counter">Counter is at: {{ counter }}</h1>
            </body>
        </html>
    """, counter=counter)

if __name__ == "__main__":
    port = os.getenv('PORT', 5000)  # Utilise le port fourni par Render, sinon 5000 par défaut
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
