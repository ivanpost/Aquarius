import requests
import math

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOiIxZmQwZDZlYi02YjZlLTVkYjYtM2IzYS1lNzk0ZmJlZTRiMGYiLCJ0aWQiOiI1NmZjZDc0ZS1kNWM5LWJmODEtZWUyYy04YWJhYWY5OTIwODUifQ.5WSJC41KFMjP5xdY2Zyo6tRHYcFruMi5ciuMNkkJdDE"

r = requests.post('https://api.lava.ru/transactions/list', headers={"Authorization": TOKEN},
                 files={"transfer_type": "withdraw", "account": 'R10031991', "period_start": "01.04.2022 0:0:0", "period_end": "24.07.2022 10:30:30"})

total = 0

for i in r.json()["items"]:
    if i['transfer_type'] == 'withdraw' and i['status'] == 'success': #and i['created_date'][6] == '7'
        print(f"[{i['created_date']}] [{i['status'].upper()}] {i['method'].replace('1', '')}{i['amount']} ")

        total += math.copysign(float(i['amount'].replace(" ", "")), int(i["method"]))

print("Total:", total)