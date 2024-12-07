from flask import Flask, render_template
import threading
import time
import os
import redis

app = Flask(__name__)

# Connexion à Redis
REDIS_URL = "redis://red-ct9pvabtq21c73brn8eg:6379"
redis_url = os.getenv(REDIS_URL, 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_url)

# Initialiser le compteur dans Redis si non existant
if not redis_client.exists('counter'):
    redis_client.set('counter', 0)

# Fonction qui incrémente le compteur toutes les 5 secondes
def increment_counter():
    while True:
        time.sleep(5)
        redis_client.incr('counter')  # Incrémenter le compteur dans Redis

# Lancer la fonction d'incrémentation dans un thread séparé
thread = threading.Thread(target=increment_counter)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    # Obtenir la valeur actuelle du compteur depuis Redis
    counter = redis_client.get('counter').decode('utf-8')
    return render_template('index.html', counter=counter)

if __name__ == '__main__':
    # Utilisation du port fourni par Render, ou 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
