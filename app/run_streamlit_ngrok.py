from pyngrok import ngrok
import subprocess
import time
import os

# === 1️⃣ Masukkan authtoken ngrok kamu di sini ===
NGROK_AUTH_TOKEN = "34XYn8YbtEMDcu6SBc9eOb6TfEA_88nUNWu5ziRRBt4mZUN8S"

# === 2️⃣ File Streamlit yang ingin dijalankan ===
APP_FILE = "app/main.py"

# === 3️⃣ Set auth token (sekali saja di awal) ===
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# === 4️⃣ Jalankan Streamlit di background ===
print("🚀 Menjalankan Streamlit...")
streamlit_proc = subprocess.Popen(["streamlit", "run", APP_FILE])

# Tunggu sebentar agar Streamlit benar-benar aktif
time.sleep(5)

# === 5️⃣ Buat tunnel ngrok ke port 8501 ===
public_url = ngrok.connect(8501)
print(f"🌐 Streamlit publik URL: {public_url.public_url}")

print("\nTekan CTRL+C untuk menghentikan semuanya.")

try:
    # biarkan proses tetap jalan
    streamlit_proc.wait()
except KeyboardInterrupt:
    print("\n🛑 Menghentikan server...")
    ngrok.kill()
    streamlit_proc.terminate()