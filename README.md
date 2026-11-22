# IoT REST API — Pertemuan 9 SIF1502

> **Mata Kuliah**: Pemrograman Internet of Things (SIF1502)  
> **Program Studi**: Sistem Informasi — UNISKA Banjarmasin  
> **Nama**  : Akhmad Sugati Wijayanto  
> **NPM**   : 2410020149 
> **Kelas** : 5 F Sistem Informasi

---

## 📁 Struktur File

```
iot-rest-api-jaya/
├── simulasi_esp32.py     ← Simulator sensor (jalankan via terminal)
├── flow_nodered.json     ← Flow Node-RED (import ke Node-RED)
├── dashboard.html        ← Web Dashboard (buka di browser)
└── README.md             ← Panduan ini
```

---

## ⚙️ Prasyarat

| Kebutuhan | Keterangan |
|-----------|------------|
| **Node-RED** | `npm install -g node-red` |
| **Mosquitto** | MQTT broker lokal (port 1883) |
| **Python 3.8+** | Untuk simulator ESP32 |
| **paho-mqtt** | `pip install paho-mqtt` |
| **Browser modern** | Chrome / Edge / Firefox |

---

## 🚀 Langkah Menjalankan

### 1 — Jalankan MQTT Broker

```bash
# Windows (jika sudah install Mosquitto)
mosquitto -v

# Ubuntu/Linux
sudo service mosquitto start
# atau
mosquitto -v
```

### 2 — Jalankan Node-RED

```bash
node-red
# Buka browser: http://localhost:1880
```

### 3 — Import Flow ke Node-RED

1. Buka `http://localhost:1880`
2. Klik menu **☰ → Import**
3. Paste seluruh isi `flow_nodered.json`
4. Klik **Import**, lalu klik **Deploy** (tombol merah kanan atas)

### 4 — Jalankan Simulator ESP32

```bash
python simulasi_esp32.py
```

Output yang diharapkan:
```
[MQTT] Terhubung ke broker (localhost:1883)
ESP32 Simulator berjalan — Ctrl+C untuk berhenti
[PUBLISH] {'suhu': 27.3, 'kelembaban': 65.1, 'led': 'OFF', 'timestamp': '...'}
```

### 5 — Buka Dashboard

Letakkan `dashboard.html` di folder static Node-RED:
- **Windows**: `C:\Users\<user>\.node-red\public\`
- **Linux**: `~/.node-red/public/`

Lalu akses: `http://localhost:1880/dashboard.html`

> **Atau** cukup buka file `dashboard.html` langsung di browser (double-click).

---

## 🔑 Autentikasi API Key

Semua endpoint memerlukan header `X-API-Key`.

| API Key | Keterangan |
|---------|------------|
| `iot-secret-2024` | Key utama (default) |
| `dev-key-123` | Key development |

Contoh dengan `curl`:
```bash
curl -H "X-API-Key: iot-secret-2024" http://localhost:1880/api/suhu
```

---

## 📡 Endpoint API

| Method | URL | Deskripsi |
|--------|-----|-----------|
| `GET`  | `/api/suhu` | Data sensor terkini |
| `GET`  | `/api/history?limit=N` | Riwayat data (maks 50) |
| `POST` | `/api/kontrol` | Kirim perintah ke aktuator |
| `GET`  | `/api/threshold` | Baca batas suhu |
| `PUT`  | `/api/threshold` | Set batas suhu |

### Contoh Request & Response

#### GET /api/suhu
```bash
curl -H "X-API-Key: iot-secret-2024" http://localhost:1880/api/suhu
```
```json
{
  "status": "success",
  "data": {
    "suhu": 28.5,
    "kelembaban": 65.0,
    "led": "OFF",
    "timestamp": "2026-11-22T10:30:00",
    "received": "2026-11-22T10:30:01.234Z"
  },
  "threshold": 30.0,
  "alert": false,
  "server_time": "2026-11-22T10:30:05.678Z"
}
```

#### POST /api/kontrol
```bash
curl -X POST http://localhost:1880/api/kontrol \
  -H "Content-Type: application/json" \
  -H "X-API-Key: iot-secret-2024" \
  -d '{"device":"lamp","action":"on"}'
```
```json
{
  "status": "success",
  "message": "Perintah berhasil dikirim",
  "sent": {"device": "lamp", "action": "on"},
  "timestamp": "2026-11-22T10:31:00.000Z"
}
```

#### PUT /api/threshold
```bash
curl -X PUT http://localhost:1880/api/threshold \
  -H "Content-Type: application/json" \
  -H "X-API-Key: iot-secret-2024" \
  -d '{"threshold": 30.5}'
```

---

## ✅ Fitur Nilai Tambah (Sudah Diimplementasi)

| No | Fitur | File |
|----|-------|------|
| 1 | **Endpoint `/api/threshold` (PUT/GET)** + notifikasi otomatis | `flow_nodered.json` |
| 2 | **Grafik real-time Chart.js** (suhu & kelembaban) | `dashboard.html` |
| 3 | **Autentikasi API Key** via header `X-API-Key` | `flow_nodered.json` + `dashboard.html` |
| 4 | **WebSocket** real-time update tanpa polling | `flow_nodered.json` + `dashboard.html` |

> *Catatan: Penyimpanan ke SQLite/InfluxDB memerlukan Node-RED node tambahan (`node-red-node-sqlite`) — lihat bagian pengembangan lanjutan di bawah.*

---

## 🔌 WebSocket

Dashboard terhubung ke `ws://localhost:1880/ws/iot` secara otomatis.

Pesan yang dikirim server:
```json
// Update sensor
{ "type": "sensor_update", "data": { "suhu": 28.5, ... } }

// Notifikasi threshold terlampaui
{ "type": "threshold_alert", "suhu": 31.2, "threshold": 30.0, "timestamp": "..." }
```

---

## 🗄️ Pengembangan Lanjutan: SQLite (Opsional)

Untuk menyimpan history ke SQLite:

1. Install node: `npm install node-red-node-sqlite` (di folder `~/.node-red/`)
2. Restart Node-RED
3. Tambahkan node `sqlite` di flow setelah `fn_simpan_sensor`
4. Query: `INSERT INTO sensor_data (suhu, kelembaban, timestamp) VALUES (?, ?, ?)`

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Dashboard "Offline" | Pastikan Node-RED dan simulator berjalan |
| `401 Unauthorized` | Periksa API key di input dashboard |
| Grafik tidak update | Periksa koneksi WebSocket (badge di kanan atas) |
| `paho-mqtt` error | Jalankan `pip install paho-mqtt --upgrade` |
| Port 1883 refused | Pastikan Mosquitto berjalan (`mosquitto -v`) |

---

## 📌 Topik MQTT

| Topik | Arah | Isi |
|-------|------|-----|
| `iot/sensor` | ESP32 → Node-RED | Data suhu, kelembaban, LED |
| `iot/kontrol` | Node-RED → ESP32 | Perintah aktuator |
| `iot/alert` | Node-RED broadcast | Notifikasi threshold terlampaui |
