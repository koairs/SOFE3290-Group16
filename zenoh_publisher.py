import asyncio
import time
import json
import random
import zenoh
import os
from kuksa_client.grpc.aio import VSSClient

# Configuration
NETWORK_MODE = os.getenv("NETWORK_MODE", "normal")

NETWORK_CONFIG = {
    'normal': {'latency': 0.01, 'packet_drop': 0.0},
    'medium': {'latency': 0.075, 'packet_drop': 0.02},
    'high':   {'latency': 0.15,  'packet_drop': 0.08},
}

HIGH_PRIORITY = {'VehicleSpeed', 'BrakePressure'}
LOW_PRIORITY  = {'EngineSpeed'}

async def main():
    # Initialize Zenoh session
    session = zenoh.open(zenoh.Config())
    pub = session.declare_publisher('vehicle/obd')

    async with VSSClient('127.0.0.1', 55555) as client:
        while True:
            # Fetch values from Kuksa Databroker
            values = await client.get_current_values([
                'Vehicle.OBD.VehicleSpeed',
                'Vehicle.OBD.CoolantTemperature',
                'Vehicle.OBD.ThrottlePosition',
                'Vehicle.OBD.EngineSpeed',
                'Vehicle.OBD.BrakePressure',
                'Vehicle.OBD.TirePressure',
            ])

            data = {}
            mapping = [
                ('VehicleSpeed',     'Vehicle.OBD.VehicleSpeed'),
                ('EngineSpeed',      'Vehicle.OBD.EngineSpeed'),
                ('ThrottlePosition', 'Vehicle.OBD.ThrottlePosition'),
                ('CoolantTemperature','Vehicle.OBD.CoolantTemperature'),
                ('BrakePressure',    'Vehicle.OBD.BrakePressure'),
                ('TirePressure',     'Vehicle.OBD.TirePressure'),
            ]

            for key, signal in mapping:
                try:
                    v = values[signal].value
                    if v is not None:
                        data[key] = v
                except KeyError:
                    pass

            config = NETWORK_CONFIG.get(NETWORK_MODE, NETWORK_CONFIG['normal'])

            # Simulate Packet Drop
            if random.random() < config['packet_drop']:
                print(f'[Zenoh Publisher] [{NETWORK_MODE.upper()}] Packet DROPPED')
                await asyncio.sleep(config['latency'])
                continue

            # Simulate Network Congestion (Priority Filtering)
            if NETWORK_MODE in ('medium', 'high'):
                suppressed = [k for k in data if k not in HIGH_PRIORITY]
                if suppressed:
                    print(f'[Zenoh Publisher] [{NETWORK_MODE.upper()}] Suppressed: {suppressed}')
                
                # Filter to keep only high priority data
                data = {k: v for k, v in data.items() if k in HIGH_PRIORITY}

            # Simulate Network Latency
            await asyncio.sleep(config['latency'])

            # Publish to Zenoh
            if data:
                pub.put(json.dumps(data))
                print(f'[Zenoh Publisher] [{NETWORK_MODE.upper()}] Published: {data}')
            
            # Brief pause to prevent CPU pegging
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping Publisher...")
