import requests
import time
import os
from datetime import datetime

auth = ('ditto', 'ditto')
THING_ID = 'org.vehicle:my-device'
BASE_URL = f'http://localhost:8080/api/2/things/{THING_ID}/features'

# Fault history for dashboard
fault_history = []

def get_feature(feature):
    try:
        r = requests.get(f'{BASE_URL}/{feature}/properties/value', auth=auth, timeout=2)
        if r.status_code == 200:
            return r.json()
        return 'N/A'
    except:
        return 'ERR'

def get_mode(speed):
    if speed == 0:
        return 'IDLE'
    elif speed <= 70:
        return 'NORMAL'
    else:
        return 'HIGH SPEED'

def classify_fault(speed, brake, tire):
    faults = []

    if isinstance(speed, (int, float)) and isinstance(brake, (int, float)):
        if speed > 100 and brake < 20:
            faults.append('High speed with low brake pressure')
        if speed > 0 and brake == 0:
            faults.append('Vehicle moving with zero brake pressure')
    if isinstance(tire, (int, float)) and tire <= 30:
        faults.append(f'Tire pressure critical ({tire} psi)')
    if isinstance(speed, (int, float)) and speed > 200:
        faults.append('Speed exceeds safe limit')

    if len(faults) == 0:
        return 'OK', 'All systems nominal', faults
    elif len(faults) == 1:
        return 'MINOR', f'WARNING: {faults[0]}', faults
    elif len(faults) == 2:
        return 'MAJOR', f'CRITICAL ALERT: {" | ".join(faults)}', faults
    else:
        return 'CATASTROPHIC', f'IMMEDIATE STOP REQUIRED', faults

def log_fault(severity, message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    fault_history.append({
        'time': timestamp,
        'severity': severity,
        'message': message,
        'unix_time': time.time()
    })
    if len(fault_history) > 5:
        fault_history.pop(0)

def faults_last_5_min():
    now = time.time()
    return len([f for f in fault_history if now - f['unix_time'] <= 300])

def most_frequent_fault():
    if not fault_history:
        return 'None'
    counts = {}
    for entry in fault_history:
        counts[entry['severity']] = counts.get(entry['severity'], 0) + 1
    return max(counts, key=counts.get)

while True:
    os.system('clear')

    speed    = get_feature('VehicleSpeed')
    engine   = get_feature('EngineSpeed')
    throttle = get_feature('ThrottlePosition')
    coolant  = get_feature('CoolantTemperature')
    brake    = get_feature('BrakePressure')
    tire     = get_feature('TirePressure')

    mode = get_mode(speed) if isinstance(speed, (int, float)) else 'N/A'
    severity, message, faults = classify_fault(speed, brake, tire)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if severity != 'OK':
        log_fault(severity, message)

    print('╔══════════════════════════════════════════════╗')
    print('║       SDV Vehicle Monitoring Dashboard       ║')
    print('╠══════════════════════════════════════════════╣')
    print(f'║  Time     : {timestamp}        ║')
    print(f'║  Mode     : {mode:<33} ║')
    print('╠══════════════════════════════════════════════╣')
    print('║  VEHICLE SIGNALS                             ║')
    print('╠══════════════════════════════════════════════╣')
    print(f'║  Vehicle Speed      : {str(speed):<23} ║')
    print(f'║  Engine Speed       : {str(engine):<23} ║')
    print(f'║  Throttle Position  : {str(throttle):<23} ║')
    print(f'║  Coolant Temp       : {str(coolant):<23} ║')
    print(f'║  Brake Pressure     : {str(brake):<23} ║')
    print(f'║  Tire Pressure      : {str(tire):<23} ║')
    print('╠══════════════════════════════════════════════╣')
    print('║  OPENSOVD DIAGNOSTICS                        ║')
    print('╠══════════════════════════════════════════════╣')
    print(f'║  Severity : {severity:<33} ║')
    print(f'║  Message  : {message[:33]:<33} ║')
    print('╠══════════════════════════════════════════════╣')
    print('║  FAULT HISTORY (last 5)                      ║')
    print('╠══════════════════════════════════════════════╣')
    print(f'║  Faults in last 5 min : {str(faults_last_5_min()):<21} ║')
    print(f'║  Most frequent fault  : {most_frequent_fault():<21} ║')

    if fault_history:
        for entry in fault_history[-3:]:
            line = f'{entry["time"]} | {entry["severity"]}'
            print(f'║  {line:<44} ║')
    else:
        print('║  No faults recorded                          ║')

    print('╚══════════════════════════════════════════════╝')
    print('  Press Ctrl+C to exit')

    time.sleep(1)
