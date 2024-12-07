from flask import Flask, render_template, request
import threading
import time
import os
import redis
import logging

app = Flask(__name__)

# Réduire les logs non nécessaires
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Limiter les logs aux erreurs uniquement

# Connexion à Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
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

@app.before_request
def skip_health_checks():
    """
    Filtrer les requêtes de health checks basées sur le User-Agent et l'URL.
    """
    user_agent = request.headers.get('User-Agent', '')
    if "Go-http-client" in user_agent or "/health" in request.path:
        app.logger.info(f"Skipping health check from {user_agent} on {request.path}")
        return '', 200  # Répondre silencieusement sans générer de logs

@app.route('/')
def index():
    # Obtenir la valeur actuelle du compteur depuis Redis
    counter = redis_client.get('counter').decode('utf-8')
    return render_template('index.html', counter=counter)

if __name__ == '__main__':
    # Utilisation du port fourni par Render, ou 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
