import requests
import json

url = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/283164601"
response = requests.get(url)
data = response.json()
print(data)
