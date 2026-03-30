import random
import time
import asyncio
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Datapoint

STUCK_THROTTLE_VALUE = 150

async def main():
    async with VSSClient('127.0.0.1', 55555) as client:
        while True:
            VehicleSpeed = random.randint(0, 255)
            EngineSpeed = random.randint(0, 7000)
            ThrottlePosition = random.randint(0, 200)
            CoolantTemperature = random.randint(0, 500)
            BrakePressure = random.randint(0, 100)
            TirePressure = random.randint(20, 50)

            # Randomly inject a fault (none is weighted higher for realism)
            FAULT_MODE = random.choice(['none', 'none', 'none', 'noisy_rpm', 'stuck_throttle', 'signal_loss'])

            fault_log = []

            # Mod 2 - Fault Injection
            if FAULT_MODE == 'noisy_rpm':
                noise = random.randint(-100, 100)
                EngineSpeed = max(0, min(7000, EngineSpeed + noise))
                fault_log.append(f'[FAULT] Noisy RPM — noise applied: {noise:+d}')
            elif FAULT_MODE == 'stuck_throttle':
                ThrottlePosition = STUCK_THROTTLE_VALUE
                fault_log.append(f'[FAULT] Stuck throttle — frozen at {STUCK_THROTTLE_VALUE}')
            elif FAULT_MODE == 'signal_loss':
                TirePressure = None
                fault_log.append('[FAULT] Signal loss — Tire pressure unavailable')

            values_to_send = {
                'Vehicle.OBD.VehicleSpeed': Datapoint(VehicleSpeed),
                'Vehicle.OBD.CoolantTemperature': Datapoint(CoolantTemperature),
                'Vehicle.OBD.ThrottlePosition': Datapoint(ThrottlePosition),
                'Vehicle.OBD.EngineSpeed': Datapoint(EngineSpeed),
                'Vehicle.OBD.BrakePressure': Datapoint(BrakePressure),
            }
            if TirePressure is not None:
                values_to_send['Vehicle.OBD.TirePressure'] = Datapoint(TirePressure)

            await client.set_current_values(values_to_send)

            # Mod 1 - Adaptive Signals
            if VehicleSpeed == 0:
                delay = 0.5
                mode = 'IDLE'
            elif VehicleSpeed <= 70:
                delay = 0.1
                mode = 'NORMAL'
            else:
                delay = 0.02
                mode = 'HIGH SPEED'

            print(f'--- Mode: {mode} | Fault: {FAULT_MODE} ---')
            print(f'  Vehicle Speed    = {VehicleSpeed}')
            print(f'  Engine Speed     = {EngineSpeed}')
            print(f'  Throttle         = {ThrottlePosition}')
            print(f'  Coolant Temp     = {CoolantTemperature}')
            print(f'  Brake Pressure   = {BrakePressure}')
            print(f'  Tire Pressure    = {TirePressure if TirePressure is not None else "UNAVAILABLE"}')
            for log in fault_log:
                print(f'  {log}')
            print('-----------------------------')

            time.sleep(1)

asyncio.run(main())
