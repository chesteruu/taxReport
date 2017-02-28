from enum import Enum
import time
import datetime


class RateData:
    rateTime = 0
    rateBid = 0.0
    rateAsk = 0.0
    seekInFile = 0

    def __init__(self, time_: int, bid_, ask_, seekInFile_):
        self.rateTime = int(time_)
        self.rateBid = float(bid_)
        self.rateAsk = float(ask_)
        self.seekInFile = int(seekInFile_)


MICROBASE = 1000
OILBASE = 10
INDEXBASE = 1
GOLDBASE = 1


class CurrencyRatioData:
    ratio = 0
    pair = ""

    def __init__(self, ratio_, pair_):
        self.ratio = ratio_
        self.pair = pair_

    def printf(self):
        print("BaseRatio: {} BasePair: {}".format(self.ratio, self.pair))


currecyRatioData = {
    'OIL': CurrencyRatioData(OILBASE, "USD_SEK"),
    'GER30': CurrencyRatioData(INDEXBASE, "EUR_SEK"),
    'US_SHARE': CurrencyRatioData(INDEXBASE, "USD_SEK"),
    'JP225': CurrencyRatioData(INDEXBASE, "USD_JPY"),
    'GOLD': CurrencyRatioData(GOLDBASE, "USD_SEK"),
    'GAS': CurrencyRatioData(INDEXBASE, "USD_SEK"),
    'UK100': CurrencyRatioData(INDEXBASE, "GBP_SEK"),
    'SILVER': CurrencyRatioData(INDEXBASE, "USD_SEK"),
    'AUS200': CurrencyRatioData(INDEXBASE, "AUD_SEK"),
    'OTHER': CurrencyRatioData(0, ""),
}


def getCurrencyRatioData(name_: str):
    if name_[:3] == "ger":
        return currecyRatioData["GER30"]
    if name_[:3] == "us3" or name_[:3] == "us5":
        return currecyRatioData["US_SHARE"]
    if name_[:3] == "uk1":
        return currecyRatioData["UK100"]
    if name_[:3] == "oil":
        return currecyRatioData["OIL"]
    if name_[:4] == "gold":
        return currecyRatioData["GOLD"]
    if name_[:4] == "jp22":
        return currecyRatioData["JP225"]
    if name_[:4] == "ngas":
        return currecyRatioData["GAS"]
    if name_[:3] == "sil":
        return currecyRatioData["SILVER"]
    if name_[:4] == "aus2":
        return currecyRatioData["AUS200"]

    forexName = name_[3:6]

    forexName = name_[:3] + "_" + forexName
    forexName = forexName.upper()
    return CurrencyRatioData(MICROBASE, forexName)


class TicketType(Enum):
    NON = -1
    BALANCE = 0
    BUY = 10
    BUY_LIMIT = 11
    SELL = 20
    SELL_LIMIT = 21
    CREDIT = 30

    @staticmethod
    def getTicketType(type_: str):
        if type_ == "balance":
            return TicketType.BALANCE
        if type_ == "buy":
            return TicketType.BUY
        if type_ == "buy limit":
            return TicketType.BUY_LIMIT
        if type_ == "sell":
            return TicketType.SELL
        if type_ == "sell limit":
            return TicketType.SELL_LIMIT
        if type_ == "credit":
            return TicketType.CREDIT


class ItemType:
    currencyType = getCurrencyRatioData("other")
    priceInSek = 0

    def __init__(self, name_: str):
        self.currencyType = getCurrencyRatioData(name_)


def convertToGainServerTime(time_: int) -> int:
    myServerTime = datetime.datetime.fromtimestamp(time_)
    gainServerTime = myServerTime + datetime.timedelta(hours=-7)
    return int(gainServerTime.timestamp())

class TicketData:
    ticketNumber = -1
    opentime = 0
    type = TicketType.NON
    size = 0
    item = ItemType("invalid")
    openprice = 0
    openpriceInSek = 0.0
    openpriceRate = 0.0
    openBaseRate = 0.0
    closetime = 0
    closeprice = 0
    closepriceInSek = 0.0
    closepriceRate = 0.0
    swap = 0
    swapInSek = 0.0
    profit = 0
    ratio = 1
    profitInSek = 0.0
    originalPair = ""
    targetValue = 0.0
    targetName = ""


    def __init__(self):
        pass

    def print(self):
        if self.type != TicketType.CREDIT and self.type != TicketType.BALANCE:
            return(
                "Ticket:{} OpenTime:{} Type:{} Size:{} OpenPrice:{} CloseTime:{} ClosePrice:{} Swap:{} Profit:{} ratio:{}".format(
                    self.ticketNumber,
                    self.opentime,
                    self.type,
                    self.size,
                    self.openprice,
                    self.closetime,
                    self.closeprice,
                    self.swap,
                    self.profit,
                    self.ratio))

    def updateValue(self, header_: str, value_: str):
        if (self.type == TicketType.BALANCE or self.type == TicketType.CREDIT) and header_ != "Type":
            return

        if header_ == "Ticket":
            self.ticketNumber = int(value_)
        if header_ == "Open Time":
            self.opentime = convertToGainServerTime(int(time.mktime(time.strptime(value_, "%Y.%m.%d %H:%M:%S"))))
        if header_ == "Type":
            self.type = TicketType.getTicketType(value_)
        if header_ == "Size":
            self.size = float(value_)
        if header_ == "Item":
            self.originalPair = value_
            value_.replace("cnh", "cny")
            self.item = ItemType(value_)
        if header_ == "Open Price":
            self.openprice = float(value_)
        if header_ == "Close Time":
            self.closetime = convertToGainServerTime(int(time.mktime(time.strptime(value_, "%Y.%m.%d %H:%M:%S"))))
        if header_ == "Close Price":
            self.closeprice = float(value_)
        if header_ == "Swap":
            self.swap = float(value_)
        if header_ == "Profit":
            self.profit = float(value_)

class TimedData:
    time = 0
    ticketNumber = -1
    isOpen = False


    def __init__(self, ticketNumber_, time_, isOpen_):
        self.ticketNumber = ticketNumber_
        self.time = int(time_)
        self.isOpen = isOpen_
