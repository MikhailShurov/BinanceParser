from threading import *

import GoogleSheets
import Parsers
import MarketVolume
import schedule

from Data import fiats
from Data import names


class Program:
    @staticmethod
    def run_parsing():
        schedule.every(30).minutes.do(Parsers.paysend_visa_mastercard)
        while True:
            schedule.run_pending()
            Parsers.parsers()

    @staticmethod
    def collect_volume():
        while True:
            MarketVolume.collect_v()

    @staticmethod
    def main():
        column_a = []
        column_b = []
        for fiat in fiats:
            column_a.append([fiat])

        for name in names:
            column_b.append([name])

        writer = GoogleSheets.Writer()
        writer.write(f"A2:A{len(column_a) + 1}", column_a)
        writer.write(f"B2:B{len(column_b) + 1}", column_b)

        t1 = Thread(target=Program.run_parsing, args=())
        t2 = Thread(target=Program.collect_volume, args=())
        t1.start()
        t2.start()
