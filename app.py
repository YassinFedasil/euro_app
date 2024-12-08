from flask import Flask, render_template, jsonify, request
import threading
import schedule
import time
import subprocess
import os
import redis
import logging
from flask import send_from_directory
from datetime import datetime

app = Flask(__name__)

# Réduire les logs non nécessaires
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Limiter les logs aux erreurs uniquement

# Connexion à Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_url)

# Initialiser les compteurs dans Redis si non existants
if not redis_client.exists('counter1'):
    redis_client.set('counter1', 0)
if not redis_client.exists('counter2'):
    redis_client.set('counter2', 0)

# Verrou pour éviter l'exécution simultanée des scripts
lock = threading.Lock()

# Fonction pour incrémenter le compteur 1
def increment_counter_1():
    with lock:
        redis_client.incr('counter1')
        current_counter1 = redis_client.get('counter1').decode('utf-8')
        print(f"Counter 1 incremented to {current_counter1}")

        # Exécuter le script Data_Export.py
        try:
            subprocess.run(['python', 'DataExport.py'], check=True)
            print("Script DataExport.py exécuté avec succès pour Counter 1.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de DataExport.py pour Counter 1 : {e}")

# Fonction pour incrémenter le compteur 2
def increment_counter_2():
    with lock:
        redis_client.incr('counter2')
        current_counter2 = redis_client.get('counter2').decode('utf-8')
        print(f"Counter 2 incremented to {current_counter2}")

        # Exécuter le script Data_Export.py
        try:
            subprocess.run(['python', 'DataGenerator.py'], check=True)
            print("Script DataGenerator.py exécuté avec succès pour Counter 2.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de DataGenerator.py pour Counter 2 : {e}")

# Planifier les incrémentations
schedule.every().wednesday.at("18:00").do(increment_counter_1)
schedule.every().saturday.at("18:00").do(increment_counter_1)

schedule.every().tuesday.at("06:00").do(increment_counter_2)
schedule.every().sunday.at("15:03").do(increment_counter_2)

# Fonction pour exécuter les tâches planifiées
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Vérification toutes les 10 secondes

# Lancer la fonction de planification dans un thread séparé
thread = threading.Thread(target=run_scheduler)
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
    # Obtenir les valeurs actuelles des compteurs depuis Redis
    counter1 = redis_client.get('counter1').decode('utf-8')
    counter2 = redis_client.get('counter2').decode('utf-8')
    return render_template('index.html', counter1=counter1, counter2=counter2)

@app.route('/counter')
def counter():
    # Obtenir les valeurs actuelles des compteurs depuis Redis
    counter1 = redis_client.get('counter1').decode('utf-8')
    counter2 = redis_client.get('counter2').decode('utf-8')
    return jsonify(counter1=counter1, counter2=counter2)

@app.route('/reset_counters', methods=['POST'])
def reset_counters():
    try:
        # Réinitialiser les compteurs à 0 dans Redis
        redis_client.set('counter1', 0)
        redis_client.set('counter2', 0)
        return jsonify({"message": "Compteurs réinitialisés"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Utilisation du port fourni par Render, ou 5000 par défaut
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
