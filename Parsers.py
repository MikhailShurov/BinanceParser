import requests
import json
from bs4 import BeautifulSoup
from datetime import date

from Data import fiats
from Data import headers
from Data import names
from Data import namesPaysend, idsPaysend

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
    visa = []

    gbp_course = requests.get(
        "https://my.transfergo.com/api/transfers/quote?&calculationBase=sendAmount&amount=1000.00&fromCountryCode=GB&toCountryCode=US&fromCurrencyCode=GBP&toCurrencyCode=USD").text
    gbp_course = json.loads(gbp_course)
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
                amount = amount / len(response["data"])

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
                    price = price[:price.find('.')] + "," + price[price.find('.') + 1:]
                    wise.append([price])
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
                    revolut.append([revolut_json["rate"]["rate"]])
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

                    transfer.append([
                        transfer_go["deliveryOptions"]["standard"]["paymentOptions"]["card"]["quote"][
                            "receivingAmount"] / gbp_course])
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
                    fin.append([fin_response["payload"]["receiver"]["amountToReceive"] / 1000])
                except:  # NOQA
                    fin.append(["Нет данных"])
            elif fiats[fiat] == "USD":
                fin.append([1.000])

            if fiats[fiat] != "USD":
                current_date = date.today()
                str_current_date = "" + str(current_date.month) + "%2F" + str(current_date.day) + "%2F" + str(
                    current_date.year)
                try:
                    visa_response = requests.get(
                        f"https://cis.visa.com/cmsapi/fx/rates?amount=1&fee=0&utcConvertedDate={str_current_date}&exchangedate={str_current_date}&fromCurr={fiats[fiat]}&toCurr=USD",
                        headers=headers).text
                    visa_response = json.loads(visa_response)
                    tmp = visa_response["convertedAmount"]
                    tmp = tmp.replace(',', '')
                    tmp = tmp.replace('.', ',')
                    visa.append([tmp])
                    # print("from visa: ", tmp, " " + str(fiats[fiat]))
                except:  # NOQA
                    visa.append(["Нет данных"])
            elif fiats[fiat] == "USD":
                visa.append([1.000])

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
    writer.write(f"M2:M{len(visa) + 1}", visa)


def paysend_visa_mastercard():
    paysend = []

    mastercard = []
    for fiat in range(len(fiats)):
        if fiats[fiat] != "USD":
            try:
                response = requests.get(
                    f'https://paysend.com/en-lv/send-money/from-the-united-states-of-america-to-{namesPaysend[fiats[fiat]]}?fromCurrId=840&toCurrId={idsPaysend[namesPaysend[fiats[fiat]]]}&isFrom=false').text
                soup = BeautifulSoup(response, 'lxml')
                price = soup.find("div", {"id": "component-fee"})
                div = price.find("span", {"class": "foo"}).text
                div = div[11:-4]
                paysend.append([div.replace('.', ',')])
                print(div)
            except:  # NOQA
                paysend.append(["Нет данных"])
        elif fiats[fiat] == "USD":
            paysend.append([1.000])

        if fiats[fiat] != "USD":
            try:
                mastercard_response = requests.get(
                    f'https://www.mastercard.ua/settlement/currencyrate/conversion-rate?fxDate=0000-00-00&transCurr=USD&crdhldBillCurr={fiats[fiat]}&bankFee=0&transAmt=1').text
                mastercard_response = json.loads(mastercard_response)
                mastercard.append([mastercard_response["data"]["conversionRate"]])
            except:  # NOQA
                mastercard.append(["Нет данных"])
        elif fiats[fiat] == "USD":
            mastercard.append([1.000])

    writer = GoogleSheets.Writer()
    writer.write(f"L2:L{len(paysend) + 1}", paysend)
    writer.write(f"N2:N{len(mastercard) + 1}", mastercard)
