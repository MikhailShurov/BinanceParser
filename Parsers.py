import requests
import json
from bs4 import BeautifulSoup

from Data import fiats
from Data import headers
from Data import names

import GoogleSheets


def parsers():
    fiats_range = []
    names_range = []
    middle_price_range = []
    nbank = [[""] for _ in range(100)]
    wise = []
    revolut = []
    transfer = []
    fin = []

    gbp_course = requests.get(
        "https://my.transfergo.com/api/transfers/quote?&calculationBase=sendAmount&amount=1000.00&fromCountryCode=GB&toCountryCode=US&fromCurrencyCode=GBP&toCurrencyCode=USD").text
    gbp_course = json.loads(gbp_course);
    gbp_course = gbp_course["deliveryOptions"]["standard"]["paymentOptions"]["card"]["quote"]["receivingAmount"]

    for fiat in range(len(fiats)):
        try:
            print(fiats[fiat])
            data = {
                "asset": "USDT",
                "countries": [],
                "fiat": fiats[fiat],
                "merchantCheck": False,
                "page": 1,
                "payTypes": [],
                "publisherType": None,
                "rows": 10,
                "tradeType": "BUY",
            }

            r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data,
                              timeout=(10, 20))
            response = json.loads(r.text)

            amount = 0
            tradable_quantity = 0
            for item in range(len(response["data"])):
                amount += float(response["data"][item]["adv"]["price"])
                tradable_quantity += float(response["data"][item]["adv"]["tradableQuantity"])
            if len(response["data"]) == 0:
                amount = "Нет данных"
            else:
                amount = round(amount / len(response["data"]), 2)

            fiats_range.append([fiats[fiat]])
            names_range.append([names[fiat]])
            middle_price_range.append([amount])

            data = {"filter": [{"left": "name", "operation": "nempty"},
                               {"left": "name,description", "operation": "match", "right": "USD"}],
                    "options": {"lang": "ru"}, "markets": ["forex"],
                    "symbols": {"query": {"types": ["forex"]}, "tickers": []},
                    "columns": ["base_currency_logoid", "currency_logoid", "name", "close", "change", "change_abs",
                                "bid", "ask", "high", "low", "Recommend.All", "description", "type", "subtype",
                                "update_mode", "pricescale", "minmov", "fractional",
                                "minmove2"], "sort": {"sortBy": "name", "sortOrder": "asc"}, "range": [0, 150]}

            data["filter"][1]["right"] = f"USD{fiats[fiat]}"

            response = requests.post("https://scanner.tradingview.com/forex/scan", json=data)
            response = json.loads(response.text)
            try:
                nbank[fiats.index(response["data"][0]["s"][10:13])] = [response["data"][0]["d"][3]]
            except:  # NOQA
                pass

            if fiats[fiat] not in ["USD", "VES"]:
                try:
                    wise_val = requests.get(
                        f'https://wise.com/ru/currency-converter/usd-to-{fiats[fiat].lower()}-rate?amount=1',
                        headers=headers, timeout=(10, 20))
                    soup = BeautifulSoup(wise_val.text, 'lxml')
                    price = soup.find("span", "text-success").text
                    price = price[:price.find('.')] + price[price.find('.') + 1:]
                    wise.append([round(float(price), 3)])
                except:  # NOQA
                    wise.append([""])
            elif fiats[fiat] == "USD":
                wise.append([1.000])
            else:
                wise.append([""])

            if fiats[fiat] != "USD":
                try:
                    revolut_json = json.loads(requests.get(
                        f'https://www.revolut.com/api/exchange/quote/?amount=1&country=GB&fromCurrency=USD&isRecipientAmount=false&toCurrency={fiats[fiat]}',
                        headers=headers).text)
                    revolut.append([round(revolut_json["rate"]["rate"], 3)])
                except:  # NOQA
                    revolut.append([""])
            elif fiats[fiat] == "USD":
                revolut.append([1.000])

            if fiats[fiat] != "USD":
                try:
                    transfer_go = requests.get(
                        f"https://my.transfergo.com/api/transfers/quote?&calculationBase=sendAmount&amount=1000.00&fromCountryCode=GB&toCountryCode={str(fiats[fiat])[:2]}&fromCurrencyCode=GBP&toCurrencyCode={fiats[fiat]}",
                        headers=headers).text
                    transfer_go = json.loads(transfer_go)

                    transfer.append([round(
                        transfer_go["deliveryOptions"]["standard"]["paymentOptions"]["card"]["quote"][
                            "receivingAmount"] / gbp_course, 3)])
                except Exception as ex:  # NOQA
                    transfer.append(["Нет данных"])
            elif fiats[fiat] == "USD":
                transfer.append([1.000])

            if fiats[fiat] != "USD":
                try:
                    data = {"amount": 1000,
                            "type": "SENDER",
                            "sender": {"sourceType": "CARD",
                                       "currency": "USD",
                                       "country": "BY"},
                            "receiver": {"sourceType": "CARD",
                                         "currency": str(fiats[fiat]),
                                         "country": str(fiats[fiat])[:2]}
                            }
                    fin_response = requests.post(
                        f'https://api.fin.do/v1/api/fin/AssumeCommission', headers=headers, json=data).text
                    fin_response = json.loads(fin_response)
                    fin.append([round(fin_response["payload"]["receiver"]["amountToReceive"] / 1000, 3)])

                except:  # NOQA
                    fin.append(["Нет данных"])
            elif fiats[fiat] == "USD":
                fin.append([1.000])

        except Exception as ex:
            print(ex, "smth went wrong...")
            continue

    writer = GoogleSheets.Writer()
    writer.write(f"C2:C{len(middle_price_range) + 1}", middle_price_range)
    writer.write(f"D2:D{len(nbank) + 1}", nbank)
    writer.write(f"F2:F{len(wise) + 1}", wise)
    writer.write(f"G2:G{len(revolut) + 1}", revolut)
    writer.write(f"J2:J{len(fin) + 1}", fin)
    writer.write(f"K2:K{len(transfer) + 1}", transfer)