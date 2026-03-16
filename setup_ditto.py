import requests
import json

auth = ('ditto', 'ditto')

# Step 1 - Create policy
with open('policy.json') as f:
    policy_data = json.load(f)

r = requests.put(
    'http://localhost:8080/api/2/policies/org.vehicle:my-policy',
    json=policy_data,
    headers={'Content-Type': 'application/json'},
    auth=auth
)
print(f'Policy creation: {r.status_code}')

# Step 2 - Create Thing
with open('VSS_Ditto.json') as f:
    thing_data = json.load(f)

r = requests.put(
    'http://localhost:8080/api/2/things/org.vehicle:my-device',
    json=thing_data,
    headers={'Content-Type': 'application/json'},
    auth=auth
)
print(f'Thing creation: {r.status_code}')

if r.status_code == 201:
    print('Setup complete! org.vehicle:my-device is ready in Ditto.')
else:
    print(f'Something went wrong: {r.text}')
