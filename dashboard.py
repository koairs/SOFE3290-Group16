import requests
import time
import os
from datetime import datetime

auth = ('ditto', 'ditto')
THING_ID = 'org.vehicle:my-device'
BASE_URL = f'http://localhost:8080/api/2/things/{THING_ID}/features'

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

while True:
    os.system('clear')

    speed = get_feature('VehicleSpeed')
    engine = get_feature('EngineSpeed')
    throttle = get_feature('ThrottlePosition')
    coolant = get_feature('CoolantTemperature')

    mode = get_mode(speed) if isinstance(speed, (int, float)) else 'N/A'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    print('╚══════════════════════════════════════════════╝')
    print('  Press Ctrl+C to exit')

    time.sleep(1)
