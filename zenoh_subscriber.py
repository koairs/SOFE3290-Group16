import zenoh
import json
import requests
import time

#Mod ditto data, vehicle marked unsafe, if specific cond occur

thingsURL = "http://localhost:8080/api/2/things/"
auth = ("ditto", "ditto")

def put_feature_value(thingID, feature, value):
    url = thingsURL + thingID + "/features/" + feature + "/properties"
    headers = {"Content-Type": "Application/json"}
    data = {"value": value}
    response = requests.put(url, json=data, headers=headers, auth=auth)
    return response

def on_message(sample):
    data = json.loads(sample.payload.to_bytes())
    print(f'[Zenoh Subscriber] Received: {data}')

    for feature, value in data.items():
        response = put_feature_value('org.vehicle:my-device', feature, value)
        print(f'  -> Sent {feature}={value} to Ditto | Response: {response.status_code}')

session = zenoh.open(zenoh.Config())
subscriber = session.declare_subscriber('vehicle/obd', on_message)

print('[Zenoh Subscriber] Listening...')
while True:
    time.sleep(1)
