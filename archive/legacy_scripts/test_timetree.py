import requests
import json
url = "http://www.timetree.org/ajax/pairwise/Homo%20sapiens/Pan%20troglodytes"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
print(resp.status_code, resp.text)
