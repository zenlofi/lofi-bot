from flask import Flask
import threading
import time

app = Flask(__name__)

def bot_loop():
    while True:
        print("Zen Lofi bot rodando...")
        time.sleep(60)

@app.route("/")
def home():
    return "Zen Lofi bot ativo"

threading.Thread(target=bot_loop).start()

app.run(host="0.0.0.0", port=10000)
