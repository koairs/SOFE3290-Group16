import zenoh
import json
import requests
import time

thingsURL = "http://localhost:8080/api/2/things/"
auth = ("ditto", "ditto")

def put_feature_value(thingID, feature, value):
    url = thingsURL + thingID + "/features/" + feature + "/properties"
    headers = {"Content-Type": "Application/json"}
    data = {"value": value}
    response = requests.put(url, json=data, headers=headers, auth=auth)
    return response

def check_safety_rules(data):
    alerts = []
    speed = data.get('VehicleSpeed', 0)
    brake = data.get('BrakePressure', 100)
    tire = data.get('TirePressure', 35)

    if speed > 100 and brake < 20:
        alerts.append('Unsafe: Speed > 100km/h and brake pressure low')

    if speed > 0 and brake == 0:
        alerts.append('Unsafe: Vehicle is moving with no brake pressure')

    if tire is not None and tire <= 30:
        alerts.append(f'Unsafe: Tire pressure is critical ({tire} psi)')

    return alerts

def on_message(sample):
    data = json.loads(sample.payload.to_bytes())
    print(f'[Zenoh Subscriber] Received: {data}')

    for feature, value in data.items():
        response = put_feature_value('org.vehicle:my-device', feature, value)
        print(f'  -> Sent {feature}={value} to Ditto | Response: {response.status_code}')

    # Run safety checks
    alerts = check_safety_rules(data)
    if alerts:
        print('Safety alerts: :')
        for alert in alerts:
            print(f'    [!!!] {alert}')
    else:
        print('Safety check passed!')

session = zenoh.open(zenoh.Config())
subscriber = session.declare_subscriber('vehicle/obd', on_message)

print('[Zenoh Subscriber] Listening...')
while True:
    time.sleep(1)
