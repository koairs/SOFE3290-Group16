import random

import time

import asyncio

from kuksa_client.grpc.aio import VSSClient

from kuksa_client.grpc import Datapoint

#FAULT_MODE='none', inc log to track sensor injection faults, simulate real world failrues
#noisy RPM, stuck throttle, signal loss, if/elif

async def main():

    async with VSSClient('127.0.0.1', 55555) as client:

        while True:

            VehicleSpeed = random.randint(0,255)

            EngineSpeed = random.randint(0,1000)

            ThrottlePosition = random.randint(0,200)

            CoolantTemperature = random.randint(0,500)

            await client.set_current_values({

                'Vehicle.OBD.VehicleSpeed': Datapoint(VehicleSpeed),

                'Vehicle.OBD.CoolantTemperature': Datapoint(CoolantTemperature),

                'Vehicle.OBD.ThrottlePosition': Datapoint(ThrottlePosition),

                'Vehicle.OBD.EngineSpeed': Datapoint(EngineSpeed),

            })

            if VehicleSpeed == 0:

                delay = 0.5

                mode = "IDLE"

            elif VehicleSpeed <= 70:

                delay = 0.1

                mode = "NORMAL"

            else:

                delay = 0.02

                mode = "HIGH SPEED"

            print(f'--- Mode: {mode} | Delay: {delay}s ---')

            print('Vehicle Speed = ', VehicleSpeed)

            print('Engine Speed = ', EngineSpeed)

            print('Throttle Position = ', ThrottlePosition)

            print('Coolant Temperature = ', CoolantTemperature)

            print('-----------------------------')

            time.sleep(1)

asyncio.run(main())

