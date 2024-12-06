from flask import Flask, render_template_string
from flask_socketio import SocketIO
import time
import threading

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
    # Démarrer le compteur dans un thread séparé
    threading.Thread(target=counter_loop, daemon=True).start()

    # Utiliser Flask-SocketIO avec le serveur de développement (en ajoutant allow_unsafe_werkzeug=True pour ignorer l'avertissement)
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
