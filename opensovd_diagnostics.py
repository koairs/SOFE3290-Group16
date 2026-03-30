# Eclipse OpenSOVD - Simulated Diagnostic Intelligence
# Modification 5: Subscribes to Zenoh, classifies faults, tracks history and response times.

import zenoh
import json
import time
from datetime import datetime

# Historical fault storage - tracks last 5 violations
fault_history = []

# Response time log
response_time_log = []

def classify_fault(data):
    speed = data.get('VehicleSpeed', 0)
    brake = data.get('BrakePressure', 100)
    tire = data.get('TirePressure', 35)

    faults = []

    # Check all fault conditions
    if speed > 100 and brake < 20:
        faults.append('High speed with low brake pressure')
    if speed > 0 and brake == 0:
        faults.append('Vehicle moving with zero brake pressure')
    if tire is not None and tire <= 30:
        faults.append(f'Tire pressure critical ({tire} psi)')
    if speed > 200:
        faults.append('Speed exceeds safe limit')

    # Classify based on number of faults
    if len(faults) == 0:
        return ('OK', 'All systems nominal')
    elif len(faults) == 1:
        return ('MINOR', f'WARNING: {faults[0]}')
    elif len(faults) == 2:
        return ('MAJOR', f'CRITICAL ALERT: {" | ".join(faults)}')
    else:
        return ('CATASTROPHIC', f'IMMEDIATE STOP REQUIRED: {" | ".join(faults)}')

def log_fault(severity, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {
        'time': timestamp,
        'severity': severity,
        'message': message,
        'unix_time': time.time()
    }
    fault_history.append(entry)
    # Keep only last 5
    if len(fault_history) > 5:
        fault_history.pop(0)

def query_last_5_minutes():
    now = time.time()
    recent = [f for f in fault_history if now - f['unix_time'] <= 300]
    return len(recent)

def most_frequent_fault():
    if not fault_history:
        return 'No faults recorded'
    counts = {}
    for entry in fault_history:
        msg = entry['severity']
        counts[msg] = counts.get(msg, 0) + 1
    return max(counts, key=counts.get)

def on_message(sample):
    # Log request timestamp
    request_time = time.time()
    request_timestamp = datetime.now().strftime('%H:%M:%S')

    data = json.loads(sample.payload.to_bytes())

    # Run diagnostics
    severity, message = classify_fault(data)

    # Log response timestamp
    response_time = time.time()
    response_timestamp = datetime.now().strftime('%H:%M:%S')
    processing_time = round((response_time - request_time) * 1000, 3)

    # Log response time
    response_time_log.append({
        'request': request_timestamp,
        'response': response_timestamp,
        'processing_ms': processing_time
    })

    # Log fault if not OK
    if severity != 'OK':
        log_fault(severity, message)

    # Print diagnostic report
    print(f'\n[OpenSOVD {request_timestamp}]')
    print(f'  Data     : {data}')
    print(f'  Severity : {severity}')
    print(f'  Message  : {message}')
    print(f'  Response Time: {processing_time}ms')

    # Print history summary
    print(f'  Faults in last 5 min : {query_last_5_minutes()}')
    print(f'  Most frequent fault  : {most_frequent_fault()}')

    if fault_history:
        print(f'  Last {len(fault_history)} fault(s):')
        for entry in fault_history:
            print(f'    {entry["time"]} | {entry["severity"]} | {entry["message"]}')

session = zenoh.open(zenoh.Config())
subscriber = session.declare_subscriber('vehicle/obd', on_message)

print('[OpenSOVD] Diagnostic Intelligence active — listening on Zenoh...')
while True:
    time.sleep(1)
