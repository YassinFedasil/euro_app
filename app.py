from flask import Flask, render_template
import threading
import time

app = Flask(__name__)

# Variable globale pour le compteur
counter = 0

# Fonction qui incrémente le compteur toutes les 5 secondes
def increment_counter():
    global counter
    while True:
        time.sleep(5)
        counter += 1

# Lancer la fonction d'incrémentation dans un thread séparé
thread = threading.Thread(target=increment_counter)
thread.daemon = True
thread.start()

@app.route('/')
def index():
    return render_template('index.html', counter=counter)

if __name__ == '__main__':
    app.run(debug=True)
