# Simulated OpenSOVD Diagnostics
# In a full implementation, this would use the actual Eclipse OpenSOVD stack.
# For Iteration 1, this script simulates OpenSOVD's diagnostic behaviour by
# subscribing to vehicle data via Zenoh and classifying faults in real time.

import zenoh
import json
import time
from datetime import datetime

fault_history = []

def classify_fault(data):
    speed = data.get('VehicleSpeed', 0)
    engine = data.get('EngineSpeed', 0)
    throttle = data.get('ThrottlePosition', 0)
    coolant = data.get('CoolantTemperature', 0)

    faults = []

    # Coolant temperature fault
    if coolant > 400:
        faults.append(('CATASTROPHIC', 'Coolant temperature critical — immediate stop required'))
    elif coolant > 300:
        faults.append(('MAJOR', 'Coolant temperature high — check cooling system'))
    elif coolant > 200:
        faults.append(('MINOR', 'Coolant temperature elevated — monitor closely'))

    # Engine speed fault
    if engine > 900:
        faults.append(('MAJOR', 'Engine RPM dangerously high'))
    elif engine > 700:
        faults.append(('MINOR', 'Engine RPM elevated'))

    # Throttle fault
    if throttle > 180:
        faults.append(('CATASTROPHIC', 'Throttle position maxed — possible stuck throttle'))
    elif throttle > 150:
        faults.append(('MAJOR', 'Throttle position very high'))

    # Speed fault
    if speed > 200:
        faults.append(('MAJOR', 'Vehicle speed exceeds safe limit'))

    return faults

def log_fault(severity, message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = {'time': timestamp, 'severity': severity, 'message': message}
    fault_history.append(entry)

    # Keep only last 5
    if len(fault_history) > 5:
        fault_history.pop(0)

    if severity == 'CATASTROPHIC':
        print(f'  [!!!] CATASTROPHIC | {message}')
    elif severity == 'MAJOR':
        print(f'  [!!]  MAJOR        | {message}')
    elif severity == 'MINOR':
        print(f'  [!]   MINOR        | {message}')

def on_message(sample):
    data = json.loads(sample.payload.to_bytes())
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'\n[OpenSOVD {timestamp}] Analysing: {data}')

    faults = classify_fault(data)

    if not faults:
        print('  [OK] No faults detected')
    else:
        for severity, message in faults:
            log_fault(severity, message)

    # Print fault history summary
    if fault_history:
        print(f'  [History] Last {len(fault_history)} fault(s):')
        for entry in fault_history:
            print(f'    {entry["time"]} | {entry["severity"]} | {entry["message"]}')

session = zenoh.open(zenoh.Config())
subscriber = session.declare_subscriber('vehicle/obd', on_message)

print('[OpenSOVD] Diagnostic monitor active — listening on Zenoh...')
while True:
    time.sleep(1)
