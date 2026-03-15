import asyncio
from kuksa_client.grpc.aio import VSSClient
import time
import json
import requests

thingsURL = "http://localhost:8080/api/2/things/"
policiesURL = "http://localhost:8080/api/2/policies/"
auth = ("ditto", "ditto")

def get_thing(thingID):
    url = thingsURL + thingID
    response = requests.get(url, auth=auth)
    if response.status_code == 404:
        return None
    else:
        return response.json()

def put_thing(thingID, ThingData):
    thing = get_thing(thingID)
    url = thingsURL + thingID
    if thing is None:
        headers = {"Content-Type": "Application/json"}
        response = requests.put(url, json=ThingData, headers=headers, auth=auth)
        return response
    else:
        print("There is a thing already created with the same thingID")
        print("Do you want to overwrite it (y/n)?")
        answer = input()
        if answer.lower() == 'y':
            headers = {"Content-Type": "Application/json"}
            response = requests.put(url, json=ThingData, headers=headers, auth=auth)
            return response

def patch_thing(thingID, ThingData):
    url = thingsURL + thingID
    headers = {"Content-Type": "Application/merge-patch+json"}
    response = requests.patch(url, json=ThingData, headers=headers, auth=auth)
    return response

def delete_thing(thingID):
    url = thingsURL + thingID
    response = requests.delete(url, auth=auth)
    return response

def put_policy(policyID, PolicyData):
    url = policiesURL + policyID
    headers = {"Content-Type": "Application/json"}
    response = requests.put(url, json=PolicyData, headers=headers, auth=auth)
    return response.json()

def delete_policy(policyID):
    url = policiesURL + policyID
    response = requests.delete(url, auth=auth)
    if response.status_code == 204:
        print(f"Policy '{policyID}' successfully deleted.")
    else:
        print(f"Failed to delete policy '{policyID}'. Status code: {response.status_code}, Response: {response.text}")
    return response

def get_feature_value(thingID, feature):
    url = thingsURL + thingID + "/features/" + feature + "/properties/value"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        value = float(response.json())
        return value
    else:
        return response

def put_feature_value(thingID, feature, value):
    url = thingsURL + thingID + "/features/" + feature + "/properties"
    headers = {"Content-Type": "Application/json"}
    data = {"value": value}
    response = requests.put(url, json=data, headers=headers, auth=auth)
    return response

async def main():
    async with VSSClient('127.0.0.1', 55555) as client:
        while True:
            values = await client.get_current_values([
                'Vehicle.OBD.VehicleSpeed',
                'Vehicle.OBD.CoolantTemperature',
                'Vehicle.OBD.ThrottlePosition',
                'Vehicle.OBD.EngineSpeed'
            ])
            VehicleSpeed = values['Vehicle.OBD.VehicleSpeed'].value
            EngineSpeed = values['Vehicle.OBD.EngineSpeed'].value
            ThrottlePosition = values['Vehicle.OBD.ThrottlePosition'].value
            CoolantTemperature = values['Vehicle.OBD.CoolantTemperature'].value

            print('VehicleSpeed = ', VehicleSpeed)
            response = put_feature_value('org.vehicle:my-device', 'VehicleSpeed', VehicleSpeed)
            print(response)

            print('EngineSpeed = ', EngineSpeed)
            response = put_feature_value('org.vehicle:my-device', 'EngineSpeed', EngineSpeed)
            print(response)

            print('ThrottlePosition = ', ThrottlePosition)
            response = put_feature_value('org.vehicle:my-device', 'ThrottlePosition', ThrottlePosition)
            print(response)

            print('CoolantTemperature = ', CoolantTemperature)
            response = put_feature_value('org.vehicle:my-device', 'CoolantTemperature', CoolantTemperature)
            print(response)

            time.sleep(1)
            print('-----------------------------')

asyncio.run(main())
