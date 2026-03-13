import os
import time
import subprocess
import threading

from flask import Flask
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.common.by import By
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# -----------------------------
# CONFIG
# -----------------------------

TRACKS_DIR = "tracks"
VIDEO_DIR = "videos"
PROMPT = "lofi chill beat relaxing study music instrumental"

# -----------------------------
# 1 GERAR MUSICA NO SUNO
# -----------------------------
def generate_music():
    driver = webdriver.Chrome()
    driver.get("https://suno.ai")
    time.sleep(10)
    
    prompt = driver.find_element(By.TAG_NAME,"textarea")
    prompt.send_keys(PROMPT)
    generate = driver.find_element(By.TAG_NAME,"button")
    generate.click()
    time.sleep(120)

    download = driver.find_element(By.XPATH,"//a[contains(@href,'.mp3')]")
    download.click()
    driver.quit()

# -----------------------------
# 2 VERIFICAR DURACAO
# -----------------------------
def get_total_duration():
    total = 0
    
    for file in os.listdir(TRACKS_DIR):
        if file.endswith(".mp3"):
            audio = AudioSegment.from_mp3(
                os.path.join(TRACKS_DIR,file)
            )
            total += len(audio)
    return total

# -----------------------------
# 3 JUNTAR MUSICAS
# -----------------------------
def create_mix():
    files = []

    for file in os.listdir(TRACKS_DIR):
        if file.endswith(".mp3"):
            files.append(file)

    with open("list.txt","w") as f:
        for track in files:
            f.write(f"file '{TRACKS_DIR}/{track}'\n")

    subprocess.run([
        "ffmpeg",
        "-f","concat",
        "-safe","0",
        "-i","list.txt",
        "-c","copy",
        "mix.mp3"
    ])

# -----------------------------
# 4 CRIAR VIDEO
# -----------------------------
def create_video():
    subprocess.run([
        "ffmpeg",
        "-stream_loop","-1",
        "-i","background.mp4",
        "-i","mix.mp3",
        "-shortest",
        "-c:v","libx264",
        "-c:a","aac",
        f"{VIDEO_DIR}/lofi_video.mp4"
    ])

# -----------------------------
# 5 UPLOAD YOUTUBE
# -----------------------------
def upload_youtube():
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    youtube = build("youtube","v3",credentials=credentials)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet":{
                "title":"Lofi Beats to Study and Relax | 2 Hour Mix",
                "description":"Relaxing lofi beats for studying, sleeping and focus.",
                "tags":["lofi","study","relax","sleep"]
            },
            "status":{
                "privacyStatus":"public"
            }
        },
        media_body=MediaFileUpload(
            f"{VIDEO_DIR}/lofi_video.mp4"
        )
    )

    request.execute()

# -----------------------------
# LOOP DO BOT
# -----------------------------
def bot_loop():
    while True:
        print("Gerando música...")
        generate_music()
        print("Verificando duração...")
        total = get_total_duration()
        
        if total >= 7200000:
            print("Criando mix...")
            create_mix()

            print("Criando video...")
            create_video()

            print("Enviando para youtube...")
            upload_youtube()

        time.sleep(3600)

# -----------------------------
# SERVIDOR FLASK
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Zen Lofi bot ativo"

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
