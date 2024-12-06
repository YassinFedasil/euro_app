import os
import time
from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Configuration de SocketIO
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")  # Permet toutes les origines (ajuste selon tes besoins)

# Initialisation du compteur
counter = 0

@app.route('/')
def index():
    return render_template('index.html')  # Crée un fichier index.html dans le dossier templates

# Fonction pour incrémenter le compteur automatiquement
def increment_counter():
    global counter
    while True:
        time.sleep(5)  # Attendre 5 secondes
        counter += 1
        socketio.emit('counter_update', {'counter': counter}, room=None)  # Diffuser à tous les clients

@socketio.on('increment')
def handle_increment():
    global counter
    counter += 1
    emit('counter_update', {'counter': counter}, broadcast=True)  # Envoie la nouvelle valeur du compteur à tous les clients

if __name__ == "__main__":
    # Démarrer un thread pour incrémenter le compteur toutes les 5 secondes
    thread = Thread(target=increment_counter)
    thread.daemon = True
    thread.start()

    # Lancer l'application Flask
    port = os.getenv('PORT', 5000)  # Utilise le port fourni par Render, sinon 5000 par défaut
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
