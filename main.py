import json
import requests

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from threading import *

from bs4 import BeautifulSoup

spreadsheet_id = '1s1iQV4ywYQbHsHOWOjOdQczpDiuBgbC6G4vKSZDpQnw'
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json',
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpauth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpauth)

service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Основа!A1:C2",
             "majorDimension": "COLUMNS",
             "values": [["Код валюты"], ["Название валюты"], ["Цена р2р Бинанс"]]
             }
        ]
    }
).execute()

fiats = ["AED", "AFN", "AMD", "ARS", "AUD", "AZN", "BDT", "BGN", "BHD", "BIF", "BND", "BOB", "BRL", "CAD", "CHF", "CLP", "CNY", "COP", "CRC", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ETB", "EUR", "GBP", "GEL", "GHS", "GNF", "GTQ", "HKD", "HNL",
         "HRK", "HUF", "IDR", "INR", "ISK", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KWD", "KZT", "LAK", "LBP", "LKR", "LYD", "MAD", "MDL", "MGA", "MMK", "MNT", "MOP", "MXN", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP",
         "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SCR", "SDG", "SEK", "THB", "TJS", "TMT", "TND", "TRY", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES", "VND", "XAF", "XOF", "YER", "ZAR"]
names = ["Дирхам ОАЭ", "Афганский афгани", "Армянский драм", "Аргентинское песо", "Австралийский доллар", "Азербайджанский манат", "Бангладешская така", "Болгарский лев", "Бахрейнский динар", "Бурундийский франк", "Брунейский доллар",
         "Боливийский боливиано", "Бразильский реал", "Канадский доллар", "Швейцарский франк", "Чилийское песо", "Китайский юань", "Колумбийское песо", "Коста-риканский колон", "Чешская крона", "Франк Джибути", "Датская крона",
         "Доминиканское песо", "Алжирский динар", "Египетский фунт", "Эфиопский быр", "Евро", "Фунт стерлингов", "Грузинский лари", "Ганский седи", "Гвинейский франк", "Гватемальский кетсаль", "Гонконгский доллар", "Гондурасская лемпира",
         "Хорватская куна", "Венгерский форинт",
         "Индонезийская рупия", "Индийская рупия", "Исландская крона", "Иорданский динар", "Японская иена", "Кенийский шиллинг", "Киргизский сом", "Камбоджийский риель", "Коморский франк", "Кувейтский динар", "Казахстанский тенге",
         "Лаосский кип", "Ливанский фунт", "Шри-ланкийская рупия", "Ливийский динар", "Марокканский дирхам", "Молдавский лей", "Малагасийский ариари", "Мьянманский кьят", "Монгольский тугрик", "Патака Макао", "Мексиканское песо",
         "Нигерийская найра", "Никарагуанская кордоба", "Норвежская крона", "Непальская рупия", "Новозеландский доллар", "Оманский риал", "Панамский бальбоа", "Перуанский соль", "Кина", "Филиппинское песо", "Пакистанская рупия",
         "Польский злотый", "Парагвайский гуарани", "Катарский риал",
         "Румынский лей", "Сербский динар", "Российский рубль", "Франк Руанды", "Саудовский риял", "Сейшельская рупия", "Суданский фунт", "Шведская крона", "Тайский бат", "Таджикский сомони", "Туркменский манат", "Тунисский динар",
         "Турецкая лира", "Новый тайваньский доллар", "Танзанийский шиллинг", "Украинская гривна", "Угандийский шиллинг", "Доллар США", "Уругвайское песо", "Узбекский сум", "Венесуэльский боливар", "Вьетнамский донг",
         "Центральноафриканский франк КФА", "Западноафриканский франк КФА", "Йеменский риал", "Южноафриканский рэнд"]

headers = {
    "accept-language": "ru",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

payment_types = ["BANK", "ABank", "SpecificBank", "MTBank", "PriorBank", "ParitetBank", "AbsolutBank", "IdeaBank", "Mobiletopup", "QIWI"]


def parse_binance_p2p():
    fiats_range = []
    names_range = []
    middle_price_range = []
    nbank = []
    wise = []
    revolut = []

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

            r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data, timeout=(10, 20))
            response = json.loads(r.text)

            amount = 0
            tradable_quantity = 0
            for item in range(len(response["data"])):
                amount += float(response["data"][item]["adv"]["price"])
                tradable_quantity += float(response["data"][item]["adv"]["tradableQuantity"])
            amount = round(amount / len(response["data"]), 2)

            fiats_range.append([fiats[fiat]])
            names_range.append([names[fiat]])
            middle_price_range.append([amount])


            try:
                response = requests.get(f'https://www.investing.com/currencies/usd-{fiats[fiat].lower()}', headers=headers)
                nbank_value = str(BeautifulSoup(response.text, 'lxml').find("span", "text-2xl").text)
                try:
                    nbank_value = nbank_value.replace(',', '')
                except:
                    pass
                mod_value = nbank_value.replace('.', ',')
                nbank.append([mod_value])
            except:
                nbank.append([""])

            if fiats[fiat] not in ["USD", "VES"]:
                try:
                    wise_val = requests.get(f'https://wise.com/ru/currency-converter/usd-to-{fiats[fiat].lower()}-rate?amount=1', headers=headers, timeout=(10, 20))
                    soup = BeautifulSoup(wise_val.text, 'lxml')
                    price = soup.find("span", "text-success").text
                    wise.append([price])
                except:
                    wise.append([""])
            elif fiats[fiat] == "USD":
                wise.append([1.000])
            else:
                wise.append([""])

            if fiats[fiat] != "USD":
                try:
                    revolut_json = json.loads(requests.get(f'https://www.revolut.com/api/exchange/quote/?amount=1&country=GB&fromCurrency=USD&isRecipientAmount=false&toCurrency={fiats[fiat]}', headers=headers).text)
                    revolut.append([round(revolut_json["rate"]["rate"], 3)])
                except:
                    revolut.append([""])
            elif fiats[fiat] == "USD":
                revolut.append([1.000])

        except Exception as ex:
            print(ex, "smth went wrong...")
            continue

    write("A2:G100", [["" for _ in range(4)] for _ in range(99)])
    write("F2:G100", [["" for _ in range(2)] for _ in range(99)])

    write(f"A2:A{len(fiats_range) + 1}", fiats_range)
    write(f"B2:B{len(names_range) + 1}", names_range)
    write(f"C2:C{len(middle_price_range) + 1}", middle_price_range)
    write(f"D2:D{len(nbank) + 1}", nbank)
    write(f"F2:F{len(wise) + 1}", wise)
    write(f"G2:G{len(revolut) + 1}", revolut)


def count_number(fiat):
    data = {
        "asset": "USDT",
        "countries": [],
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "publisherType": None,
        "rows": None,
        "tradeType": "BUY",
    }
    num = 1
    try:
        while True:
            data["rows"] = num
            r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
            response = json.loads(r.text)
            if response["message"] == "Please check the input info":
                return int(num - 1)
            else:
                num += 1
    except:
        return 10


def collect_v():
    tr_quantity = []
    for fiat in range(len(fiats)):
        try:
            print(fiats[fiat])
            max_num = count_number(fiats[fiat])
            data = {
                "asset": "USDT",
                "countries": [],
                "fiat": fiats[fiat],
                "merchantCheck": False,
                "page": 1,
                "payTypes": [],
                "publisherType": None,
                "rows": max_num,
                "tradeType": "BUY",
            }

            r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data, timeout=(10, 20))
            response = json.loads(r.text)

            tradable_quantity = 0
            for item in range(len(response["data"])):
                tradable_quantity += float(response["data"][item]["adv"]["tradableQuantity"])
            print(round(tradable_quantity, 3))
            tr_quantity.append([round(tradable_quantity, 3)])
        except:
            tr_quantity.append([""])
            continue

    write(f"I2:G{len(tr_quantity) + 1}", tr_quantity)


def write(ranged, data):
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "Основа!" + ranged,
                 "majorDimension": "ROWS",
                 "values": data
                 }
            ]
        }
    ).execute()


def run_parsing():
    while True:
        parse_binance_p2p()


def collect_volume():
    while True:
        collect_v()


if __name__ == '__main__':
    t1 = Thread(target=run_parsing, args=())
    t2 = Thread(target=collect_volume, args=())
    t1.start()
    t2.start()
