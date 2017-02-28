import urllib.request
import urllib.error
import urllib
import time
import datetime
import zipfile
import os
import CsvReader
import math
import json
import TicketData


def dataAssembler(currencyPair_: str, date_: datetime.datetime, rateDataList_: dict) -> TicketData.RateData:
    apiurl = "http://api.fixer.io/"
    date = date_.strftime("%Y-%m-%d")
    base = currencyPair_[:3]
    symbols = currencyPair_[-3:]
    requestUrl = apiurl + date + "?" + "base=" + base + "&symbols=" + symbols

    retryCounter = 10
    while retryCounter > 0:
        try:
            response = urllib.request.urlopen(requestUrl)
            data = json.loads(response.read())
            rate = float(data["rates"][symbols])
            return TicketData.RateData(date_.timestamp(), rate, rate, 0)
        except Exception:
            print("Request Failed with {}".format(requestUrl))
            time.sleep(1)
            retryCounter -= 1
            continue



