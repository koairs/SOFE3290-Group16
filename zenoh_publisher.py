import asyncio
import time
import json
import zenoh
from kuksa_client.grpc.aio import VSSClient

async def main():
    session = zenoh.open(zenoh.Config())
    pub = session.declare_publisher('vehicle/obd')

    async with VSSClient('127.0.0.1', 55555) as client:
        while True:
            values = await client.get_current_values([
                'Vehicle.OBD.VehicleSpeed',
                'Vehicle.OBD.CoolantTemperature',
                'Vehicle.OBD.ThrottlePosition',
                'Vehicle.OBD.EngineSpeed'
            ])

            data = {
                'VehicleSpeed': values['Vehicle.OBD.VehicleSpeed'].value,
                'EngineSpeed': values['Vehicle.OBD.EngineSpeed'].value,
                'ThrottlePosition': values['Vehicle.OBD.ThrottlePosition'].value,
                'CoolantTemperature': values['Vehicle.OBD.CoolantTemperature'].value,
            }

            pub.put(json.dumps(data))
            print(f'[Zenoh Publisher] Published: {data}')
            time.sleep(1)

asyncio.run(main())
