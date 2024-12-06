from flask import Flask
import threading
import time

app = Flask(__name__)
counter = 0

def counter_loop():
    global counter
    while True:
        counter += 1
        print(f"Counter: {counter}")
        time.sleep(5)

@app.route("/")
def home():
    return f"Counter is at: {counter}"

if __name__ == "__main__":
    threading.Thread(target=counter_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
