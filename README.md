# SOFE 3290U - Group 16 - Iteration 1: Baseline SDV Pipeline

integrating zenoh + OpenSOVD



Steps: (fix format)
clone repo: 
git clone https://github.com/koairs/SOFE3290-Group16.git
cd SOFE3290-Group16

clone kuksa: 
git clone https://github.com/eclipse-kuksa/kuksa-databroker ~/kuksa-databroker

copy files into kuksa:
mkdir -p ~/kuksa-databroker/kuksa-ditto
cp *.py ~/kuksa-databroker/kuksa-ditto/
cp VSS_Ditto.json policy.json ~/kuksa-databroker/kuksa-ditto/
cp OBD.json ~/kuksa-databroker/

Python virtual env (rules from ta):
cd ~/kuksa-databroker/kuksa-ditto
python3 -m venv venv
source venv/bin/activate
pip install kuksa-client requests

launch ditto (availible at http://localhost:8080):
git clone https://github.com/eclipse-ditto/ditto ~/ditto
cd ~/ditto/deployment/docker/
docker compose up -d

set up digital twin:
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
python3 setup_ditto.py

set up zenoh middleware
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
pip install eclipse-zenoh


^initial setup, from there you need three terminals
terminal 1: kuksa databroker
cd ~/kuksa-databroker
docker run --rm -it -p 55555:55555 \
  -v "$(pwd)/OBD.json:/OBD.json" \
  ghcr.io/eclipse-kuksa/kuksa-databroker:main \
  --insecure --vss /OBD.json

terminal 2/3/4:
cd ~/kuksa-databroker/kuksa-ditto
source venv/bin/activate
python3 send_obd_data_to_kuksa.py // python3 zenoh_publisher.py // python3 zenoh_subscriber.py


functional mod: Adaptive Signals (work in progress)
in send_OBD_data_to_kuksa.py


  
