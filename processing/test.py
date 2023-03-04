import requests
import pybase64


cred = 'yvisidorova@gmail.com:030413052409'
cred_enc = pybase64.b64encode(cred.encode()).decode('utf-8')
headers = {"Authorization": f"Basic {cred_enc}"}
response = requests.get("https://api.work.ua/jobs/atb", headers=headers)

print(response.status_code)



