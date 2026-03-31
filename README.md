# SOFE 3290U - Group 16 - Iteration 2: Baseline SDV Pipeline

## Overview
A simulated Software-Defined Vehicle (SDV) data pipeline using Eclipse Kuksa, Eclipse Zenoh, and Eclipse Ditto.
Vehicle OBD data is generated, sent to Kuksa, transported through Zenoh middleware, and displayed in a Ditto digital twin in real time along with a live monitoring dashboard.

## System Architecture
```
OBD Simulator → Kuksa (port 55555) → Zenoh Publisher → Zenoh Subscriber → Ditto (port 8080)
                                             ↓                                      ↓
                                   OpenSOVD Diagnostics                        Dashboard
```

## Components
| Component | Role |
|---|---|
| Eclipse Kuksa | Vehicle data abstraction layer |
| Eclipse Zenoh | Middleware communication layer |
| Eclipse Ditto | Digital twin and backend state management |
| OpenSOVD (simulated) | Diagnostic fault classification and health monitoring |
| Dashboard | Live terminal monitoring and visualization interface |

## Requirements
- WSL/Linux Environment
- Docker & Docker Compose
- Python 3.10+
- Git
- Python Packages
  - Kuksa-client
  - Eclipse-Zenoh
  - Requests

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
sudo apt install python3-pip
source venv/bin/activate
pip install kuksa-client requests eclipse-zenoh
```

### 5. Launch Eclipse Ditto
```
git clone https://github.com/eclipse-ditto/ditto ~/ditto
cd ~/ditto/deployment/docker/
sudo docker compose up -d
```
Ditto will be available at http://localhost:8080 (username: ditto, password: ditto)

### 6. Set up the Ditto Digital Twin (run once)
```
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
python3 setup_ditto.py
```

---

## Running the Pipeline

You need 5 terminals. Activate the venv in terminals 2-5:
```
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
```

**Terminal 1 — Kuksa Databroker:**
```
cd ~/kuksa-databroker
sudo docker run --rm -it -p 55555:55555 \
  -v "$(pwd)/kuksa-ditto/OBD.json:/OBD.json" \
  ghcr.io/eclipse-kuksa/kuksa-databroker:main \
  --insecure --metadata /OBD.json

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
**Terminal 5 — OpenSOVD Diagnostics**
```
python3 opensovd_diagnostics.py
```
**Terminal 6 — Live Monitoring Dashboard:**
```
python3 dashboard.py
```
---

## Verifying It Works
- Terminal 2 prints vehicle values with the current mode (IDLE / NORMAL / HIGH SPEED)
- Terminal 3 prints data being published to Zenoh
- Terminal 4 prints data received from Zenoh with a 204 response from Ditto
- Terminal 5 shows OpenSOVD diagnostics
- Terminal 6 shows a live updating dashboard with current vehicle signals and fault status
- Open http://localhost:8080, navigate to the Ditto UI, and confirm org.vehicle:my-device is updating in real time

---
## Functional Modifications

### Modification 1 — Adaptive Signals
Implemented in `send_obd_data_to_kuksa.py`.
Signal update rate dynamically adjusts based on vehicle speed:

| Speed | Mode | Update Rate |
|---|---|---|
| 0 km/h | IDLE | every 500ms |
| 1 – 70 km/h | NORMAL | every 100ms |
| 71+ km/h | HIGH SPEED | every 20ms |

### Modification 2 — Sensor Fault Injection
Implemented in `send_obd_data_to_kuksa.py`.
Randomly injects one of three sensor faults each iteration:

| Fault | Description |
|---|---|
| `noisy_rpm` | Adds random noise to engine speed to simulate a degraded sensor |
| `stuck_throttle` | Freezes throttle position at 150 to simulate a stuck sensor |
| `signal_loss` | Sets tire pressure to unavailable to simulate a lost signal |

Normal operation is weighted more heavily so faults occur realistically rather than constantly.

### Modification 3 — Engine Safety Rules
Implemented in `zenoh_subscriber.py`.
Checks incoming data against safety rules and triggers alerts:

| Condition | Alert |
|---|---|
| Speed > 100 km/h and brake pressure < 20 | High speed with low brake pressure |
| Speed > 0 and brake pressure = 0 | Vehicle moving with zero brake pressure |
| Tire pressure <= 30 psi | Tire pressure critical |

### Modification 4 — Network Behavior Control
Implemented in `zenoh_publisher.py`.
Simulates real-world network conditions with three configurable modes:

| Mode | Latency | Packet Drop | Filtering |
|---|---|---|---|
| `normal` | 10ms | 0% | None |
| `medium` | 75ms | 2% | Suppresses low priority signals (RPM) |
| `high` | 150ms | 8% | Suppresses low priority signals (RPM) |

Change `NETWORK_MODE` at the top of `zenoh_publisher.py` to switch modes.

### Modification 5 — Diagnostic Intelligence (OpenSOVD)
Implemented in `opensovd_diagnostics.py` and `dashboard.py`.
Provides real-time diagnostic reasoning on vehicle data via Zenoh:

**Fault Severity Classification:**

| Faults Detected | Severity | Response |
|---|---|---|
| 0 | OK | All systems nominal |
| 1 | MINOR | Warning |
| 2 | MAJOR | Critical Alert |
| 3+ | CATASTROPHIC | Immediate Stop Required |

**Historical Fault Queries:**
- Tracks last 5 safety violations
- Reports number of unsafe events in the last 5 minutes
- Reports most frequent fault type

**Diagnostic Response Time Tracker:**
- Logs request timestamp, response timestamp, and processing time for every diagnostic cycle

---
