cat > ~/kuksa-databroker/kuksa-ditto/README.md << 'EOF'
# SOFE 3290U - Group 16 - Iteration 1: Baseline SDV Pipeline

## Overview
A simulated Software-Defined Vehicle (SDV) data pipeline built using Eclipse Kuksa and Eclipse Ditto.
Vehicle OBD data is generated, sent to the Kuksa databroker, and forwarded to a Ditto digital twin in real time.

This iteration includes the Adaptive Signals modification — the signal update rate automatically
adjusts based on vehicle speed, simulating real-world vehicular data transmission behaviour.

## System Architecture
```
OBD Simulator → Eclipse Kuksa (port 55555) → Python Bridge → Eclipse Ditto (port 8080)
```

## Requirements
- Docker + Docker Compose
- Python 3
- Git

---

## Installation & Setup

### 1. Clone this repository
```
git clone https://github.com/koairs/SOFE3290-Group16.git
cd SOFE3290-Group16
```

### 2. Clone the Kuksa Databroker
```
git clone https://github.com/eclipse-kuksa/kuksa-databroker ~/kuksa-databroker
```

### 3. Copy project files into the Kuksa folder
```
mkdir -p ~/kuksa-databroker/kuksa-ditto
cp *.py ~/kuksa-databroker/kuksa-ditto/
cp VSS_Ditto.json policy.json ~/kuksa-databroker/kuksa-ditto/
cp OBD.json ~/kuksa-databroker/
```

### 4. Set up the Python virtual environment
```
cd ~/kuksa-databroker/kuksa-ditto
python3 -m venv venv
source venv/bin/activate
pip install kuksa-client requests
```

### 5. Launch Eclipse Ditto
```
git clone https://github.com/eclipse-ditto/ditto ~/ditto
cd ~/ditto/deployment/docker/
docker compose up -d
```
Ditto will be available at http://localhost:8080 (username: ditto, password: ditto)

### 6. Set up the Ditto Digital Twin (run once)
```
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
python3 setup_ditto.py
```
This creates the policy and the vehicle Thing inside Ditto.

---

## Running the Pipeline

You need 3 terminals open. Activate the venv in terminals 2 and 3:
```
source ~/kuksa-databroker/kuksa-ditto/venv/bin/activate
```

**Terminal 1 — Start the Kuksa Databroker:**
```
cd ~/kuksa-databroker
docker run --rm -it -p 55555:55555 \
  -v "$(pwd)/OBD.json:/OBD.json" \
  ghcr.io/eclipse-kuksa/kuksa-databroker:main \
  --insecure --vss /OBD.json
```

**Terminal 2 — Generate and send OBD data to Kuksa:**
```
cd ~/kuksa-databroker/kuksa-ditto
python3 send_obd_data_to_kuksa.py
```

**Terminal 3 — Forward data from Kuksa to Ditto:**
```
cd ~/kuksa-databroker/kuksa-ditto
python3 send_recieved_obd_data_to_ditto.py
```

---

## Verifying It Works
- Terminal 2 should print vehicle values every second with the current mode (IDLE / NORMAL / HIGH SPEED)
- Terminal 3 should print the same values alongside a `Response [204]` for each signal
- Open http://localhost:8080 in your browser, navigate to the Ditto UI, and you should see
  `org.vehicle:my-device` updating in real time

---

## Functional Modification — Adaptive Signals
Implemented in `send_obd_data_to_kuksa.py`.

The signal update rate dynamically adjusts based on the current vehicle speed:

| Speed | Mode | Update Rate |
|---|---|---|
| 0 km/h | IDLE | every 500ms |
| 1 – 70 km/h | NORMAL | every 100ms |
| 71+ km/h | HIGH SPEED | every 20ms |

This simulates real-world behaviour where high-speed driving requires more frequent
data transmission for safety and monitoring purposes.

---

## Project Files

| File | Description |
|---|---|
| `send_obd_data_to_kuksa.py` | Generates random OBD data and sends it to Kuksa |
| `send_recieved_obd_data_to_ditto.py` | Reads from Kuksa and forwards to Ditto digital twin |
| `retrieve_obd_data_from_kuksa.py` | Retrieves and prints OBD data from Kuksa |
| `generate_random_obd_data.py` | Standalone OBD data generator |
| `OBD.json` | VSS signal definitions for the Kuksa Databroker |
| `VSS_Ditto.json` | Ditto Thing definition mapping VSS signals |
| `policy.json` | Ditto access policy for the vehicle Thing |
EOF
