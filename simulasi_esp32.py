"""
simulasi_esp32.py
Simulasi ESP32 dengan sensor DHT22 menggunakan Python + paho-mqtt
Praktikum IoT - Pertemuan 9

Install dependency:
    pip install paho-mqtt

Jalankan:
    python simulasi_esp32.py
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# ─── KONFIGURASI ──────────────────────────────────────────────
BROKER   = "localhost"
PORT     = 1883
TOPIC_SENSOR  = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
CLIENT_ID     = "ESP32-Simulator"

# Nilai awal LED
led_state = "OFF"

# ─── CALLBACK MQTT ────────────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[MQTT] Terhubung ke broker ({BROKER}:{PORT}), reason_code={reason_code}")
    client.subscribe(TOPIC_KONTROL, qos=0)
    print(f"[MQTT] Subscribe ke topik: {TOPIC_KONTROL}")

def on_message(client, userdata, msg):
    global led_state
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[KONTROL] Perintah diterima: {payload}")
        if payload.get("device") == "lamp":
            led_state = "ON" if payload.get("action") == "on" else "OFF"
            print(f"[LED] Status lampu sekarang: {led_state}")
    except Exception as e:
        print(f"[ERROR] Gagal memproses pesan kontrol: {e}")

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"[MQTT] Terputus dari broker, reason_code={reason_code}")

# ─── INISIALISASI CLIENT ──────────────────────────────────────
# Gunakan CallbackAPIVersion.VERSION2 untuk paho-mqtt >= 2.0
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)

client.on_connect    = on_connect
client.on_message    = on_message
client.on_disconnect = on_disconnect

print(f"[MQTT] Menghubungkan ke {BROKER}:{PORT} ...")
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Tunggu koneksi
time.sleep(1)

print("=" * 55)
print("  ESP32 Simulator berjalan — Ctrl+C untuk berhenti")
print("=" * 55)

# ─── LOOP UTAMA ───────────────────────────────────────────────
# Simulasi perubahan suhu naik/turun perlahan (lebih realistis)
suhu_base      = 27.0
kelembaban_base = 65.0

try:
    while True:
        # Fluktuasi kecil agar data terasa realistis
        suhu_base      += random.uniform(-0.3, 0.4)
        kelembaban_base += random.uniform(-0.5, 0.5)

        # Batasi rentang wajar
        suhu_base      = max(20.0, min(40.0, suhu_base))
        kelembaban_base = max(40.0, min(95.0, kelembaban_base))

        payload = {
            "suhu"       : round(suhu_base, 1),
            "kelembaban" : round(kelembaban_base, 1),
            "led"        : led_state,
            "timestamp"  : datetime.now().isoformat()
        }

        result = client.publish(TOPIC_SENSOR, json.dumps(payload), qos=0)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[PUBLISH] {payload}")
        else:
            print(f"[ERROR] Gagal publish, rc={result.rc}")

        time.sleep(3)

except KeyboardInterrupt:
    print("\n[INFO] Simulator dihentikan oleh pengguna.")
    client.loop_stop()
    client.disconnect()
    print("[MQTT] Koneksi ditutup.")
