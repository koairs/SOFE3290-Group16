# SOFE 3290U - Group 16 - Iteration 1: Baseline SDV Pipeline

## Overview
A simulated Software-Defined Vehicle (SDV) data pipeline using Eclipse Kuksa, Eclipse Zenoh, and Eclipse Ditto.
Vehicle OBD data is generated, sent to Kuksa, transported through Zenoh middleware, and persisted in a Ditto digital twin in real time.

## System Architecture
```
OBD Simulator → Kuksa (port 55555) → Zenoh Publisher → Zenoh Subscriber → Ditto (port 8080)
```

## Components
| Component | Role |
|---|---|
| Eclipse Kuksa | Vehicle data abstraction layer |
| Eclipse Zenoh | Middleware communication layer |
| Eclipse Ditto | Digital twin and backend state management |

---

## Installation & Setup (on WSL)

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
pip install kuksa-client requests eclipse-zenoh
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
This creates the policy and vehicle Thing inside Ditto.

---

## Running the Pipeline

You need 4 terminals. Activate the venv in terminals 2, 3, and 4:
```
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
```

**Terminal 1 — Kuksa Databroker:**
```
cd ~/kuksa-databroker
docker run --rm -it -p 55555:55555 \
  -v "$(pwd)/OBD.json:/OBD.json" \
  ghcr.io/eclipse-kuksa/kuksa-databroker:main \
  --insecure --vss /OBD.json
```

**Terminal 2 — Generate and send OBD data to Kuksa:**
```
python3 send_obd_data_to_kuksa.py
```

**Terminal 3 — Zenoh Publisher (reads from Kuksa, publishes to Zenoh):**
```
python3 zenoh_publisher.py
```

**Terminal 4 — Zenoh Subscriber (receives from Zenoh, pushes to Ditto):**
```
python3 zenoh_subscriber.py
```

---

## Verifying It Works
- Terminal 2 prints vehicle values with the current mode (IDLE / NORMAL / HIGH SPEED)
- Terminal 3 prints data being published to Zenoh
- Terminal 4 prints data received from Zenoh with a 204 response from Ditto
- Open http://localhost:8080, navigate to the Ditto UI, and confirm org.vehicle:my-device is updating in real time

---

## Functional Modification — Adaptive Signals
Implemented in `send_obd_data_to_kuksa.py`.

Signal update rate dynamically adjusts based on vehicle speed:

| Speed | Mode | Update Rate |
|---|---|---|
| 0 km/h | IDLE | every 500ms |
| 1 – 70 km/h | NORMAL | every 100ms |
| 71+ km/h | HIGH SPEED | every 20ms |

---
