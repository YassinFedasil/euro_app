from flask import Flask, render_template, jsonify,request
import threading
import schedule
import time
import subprocess
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


# Verrou pour éviter l'exécution simultanée du script
lock = threading.Lock()

# Fonction pour incrémenter le compteur et exécuter le script Data_Export.py
def increment_counter():
    with lock:
        # Incrémenter le compteur dans Redis
        redis_client.incr('counter')
        current_counter = redis_client.get('counter').decode('utf-8')
        print(f"Counter incremented to {current_counter}")  # Log pour vérifier l'incrémentation

        # Exécuter le script Data_Export.py
        try:
            subprocess.run(['python', 'Data_Export.py'], check=True)
            print("Script Data_Export.py exécuté avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de Data_Export.py : {e}")

# Planifier l'incrémentation chaque mercredi et samedi à 18h00
schedule.every().sunday.at("01:12").do(increment_counter)
schedule.every().wednesday.at("18:00").do(increment_counter)
schedule.every().saturday.at("18:00").do(increment_counter)

# Fonction pour exécuter les tâches planifiées
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Vérification toutes les 10 secondes

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

@app.route('/counter')
def counter():
    # Obtenir la valeur actuelle du compteur depuis Redis
    counter = redis_client.get('counter').decode('utf-8')
    return jsonify(counter=counter)

if __name__ == '__main__':
    # Utilisation du port fourni par Render, ou 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
