import json
import requests
from time import sleep

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


CREDENTIALS_FILE = 'credentials.json'
spreadsheet_id = '1QcjxSx8VX5yevfSUxO1ZAE62nRVTg7iY5qtUoNJCkLE'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpauth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpauth)


service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": "A1:C2",
                 "majorDimension": "COLUMNS",
                 "values": [["Код валюты", ""], ["Название валюты", ""], ["Цена р2р Бинанс", ""]]
                 }
            ]
        }
    ).execute()


def parse():
    fiats = ["AED", "AFN", "AMD", "ARS", "AUD", "AZN", "BDT", "BGN", "BHD", "BIF", "BND", "BOB", "BRL", "CAD", "CHF", "CLP", "CNY", "COP", "CRC", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ETB", "EUR", "GBP", "GEL", "GHS", "GNF", "GTQ", "HKD", "HNL", "HRK", "HUF", "IDR", "INR", "ISK", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KWD", "KZT", "LAK", "LBP", "LKR", "LYD", "MAD", "MDL", "MGA", "MMK", "MNT", "MOP", "MXN", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SCR", "SDG", "SEK", "THB", "TJS", "TMT", "TND", "TRY", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES", "VND", "XAF", "XOF", "YER", "ZAR"]
    names = ["Дирхам ОАЭ", "Афганский афгани", "Армянский драм", "Аргентинское песо", "Австралийский доллар", "Азербайджанский манат", "Бангладешская така", "Болгарский лев", "Бахрейнский динар", "Бурундийский франк", "Брунейский доллар", "Боливийский боливиано", "Бразильский реал", "Канадский доллар", "Швейцарский франк", "Чилийское песо", "Китайский юань", "Колумбийское песо", "Коста-риканский колон", "Чешская крона", "Франк Джибути", "Датская крона", "Доминиканское песо", "Алжирский динар", "Египетский фунт", "Эфиопский быр", "Евро", "Фунт стерлингов", "Грузинский лари", "Ганский седи", "Гвинейский франк", "Гватемальский кетсаль", "Гонконгский доллар", "Гондурасская лемпира", "Хорватская куна", "Венгерский форинт",
             "Индонезийская рупия", "Индийская рупия", "Исландская крона", "Иорданский динар", "Японская иена", "Кенийский шиллинг", "Киргизский сом", "Камбоджийский риель", "Коморский франк", "Кувейтский динар", "Казахстанский тенге", "Лаосский кип", "Ливанский фунт", "Шри-ланкийская рупия", "Ливийский динар", "Марокканский дирхам", "Молдавский лей", "Малагасийский ариари", "Мьянманский кьят", "Монгольский тугрик", "Патака Макао", "Мексиканское песо", "Нигерийская найра", "Никарагуанская кордоба", "Норвежская крона", "Непальская рупия", "Новозеландский доллар", "Оманский риал", "Панамский бальбоа", "Перуанский соль", "Кина", "Филиппинское песо", "Пакистанская рупия", "Польский злотый", "Парагвайский гуарани", "Катарский риал",
             "Румынский лей", "Сербский динар", "Российский рубль", "Франк Руанды", "Саудовский риял", "Сейшельская рупия", "Суданский фунт", "Шведская крона", "Тайский бат", "Таджикский сомони", "Туркменский манат", "Тунисский динар", "Турецкая лира", "Новый тайваньский доллар", "Танзанийский шиллинг", "Украинская гривна", "Угандийский шиллинг", "Доллар США", "Уругвайское песо", "Узбекский сум", "Венесуэльский боливар", "Вьетнамский донг", "Центральноафриканский франк КФА", "Западноафриканский франк КФА", "Йеменский риал", "Южноафриканский рэнд"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    fiats_range = []
    names_range = []
    middle_price_range = []

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
            for item in range(len(response["data"])):
                amount += float(response["data"][item]["adv"]["price"])
            amount = round(amount / len(response["data"]), 2)
            fiats_range.append([fiats[fiat]])
            # fiats_range.append([""])
            names_range.append([names[fiat]])
            # names_range.append([""])
            middle_price_range.append([amount])
            # middle_price_range.append([""])
        except:
            continue
    write(f"A2:A{len(fiats_range)+1}", fiats_range)
    write(f"B2:B{len(names_range)+1}", names_range)
    write(f"C2:C{len(middle_price_range)+1}", middle_price_range)

    fiats_range, names_range, middle_price_range = None, None, None


def write(ranged, data):
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": ranged,
                 "majorDimension": "ROWS",
                 "values": data
                 }
            ]
        }
    ).execute()


if __name__ == '__main__':
    while True:
        parse()
        sleep(10)
