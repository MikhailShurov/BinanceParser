import requests
import json

import GoogleSheets

from Data import fiats
from Data import headers


def count_number(fiat):
    page = 1
    data = {
        "asset": "USDT",
        "countries": [],
        "fiat": fiat,
        "merchantCheck": False,
        "page": None,
        "payTypes": [],
        "publisherType": None,
        "rows": 10,
        "tradeType": "BUY",
    }
    try:
        while True:
            data["page"] = page
            r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
            response = json.loads(r.text)
            if response["message"] == "Please check the input info":
                return page - 1
            elif len(response["data"]) == 0:
                return page - 1
            else:
                page += 1
    except: # NOQA
        return 1


def collect_v():
    tr_quantity = []
    for fiat in range(len(fiats)):
        try:
            max_page = count_number(fiats[fiat])
            tradable_quantity = 0
            for page in range(1, max_page + 1):
                data = {
                    "asset": "USDT",
                    "countries": [],
                    "fiat": fiats[fiat],
                    "merchantCheck": False,
                    "page": page,
                    "payTypes": [],
                    "publisherType": None,
                    "rows": 10,
                    "tradeType": "BUY",
                }

                r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers,
                                  json=data, timeout=(10, 20))
                response = json.loads(r.text)

                for item in range(len(response["data"])):
                    tradable_quantity += float(response["data"][item]["adv"]["tradableQuantity"])
            print(fiats[fiat], round(tradable_quantity, 3))
            tr_quantity.append([round(tradable_quantity, 3)])
        except: # NOQA
            tr_quantity.append(["Нет предложений"])
            continue
    writer = GoogleSheets.Writer()
    writer.write(f"I2:I{len(tr_quantity) + 1}", tr_quantity)
