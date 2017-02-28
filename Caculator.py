import CsvReader
import sys
import RateFetcher
import TicketData
import datetime
import operator
import multiprocessing
import time
import os
import re

saveFileTo = "K:/Data/"
saveCsvFileTo = saveFileTo + "result/"

def work(chunkData: dict, num, resultQueue_, index):
    #sys.stderr = open(saveCsvFileTo + str(num) + "_error.out", "w")
    resultQueue_.put("Worker {} start! index = {}".format(num, index))
    filename = saveCsvFileTo + "BLANKETTER.SRU." + str(num)
    file = open(filename, "wt")
    Runner.__call__(chunkData, resultQueue_, file, num)
    # BLANKETTSLUT
    # FIL_SLUT
    file.write("#BLANKETTSLUT\n")
    #file.write("#FIL_SLUT")

    file.flush()
    file.close()
    resultQueue_.put("Worker {} Finished!".format(num))


def calculateForex(isOpen, dealPrice, baseActualRate, dealSize, dealRatio, openBaseRate = 0.0):
    if isOpen:
        rateToSEK = dealPrice / baseActualRate
        totalPrice = dealPrice * dealSize * dealRatio / rateToSEK
    else:
        totalPrice = dealPrice * dealSize * dealRatio / openBaseRate

    return totalPrice

class Runner:
    ticketDataDict = {"", ""}
    # for ticketData in ticketDataList:
    #    ticketData.print()
    # RateFetcher.fileFetcher("EUR_SEK")
    timedSeriseVector = []
    num = 0


    def constructTimeSeriseVector(self):

        for ticketNumber in self.ticketDataDict.keys():
            if self.ticketDataDict[ticketNumber].opentime == 0:
                continue
            if self.ticketDataDict[ticketNumber].closetime == 0:
                continue

            self.timedSeriseVector.append(
                TicketData.TimedData(ticketNumber, self.ticketDataDict[ticketNumber].opentime, True))
            self.timedSeriseVector.append(
                TicketData.TimedData(ticketNumber, self.ticketDataDict[ticketNumber].closetime, False))

        self.timedSeriseVector.sort(key=lambda data: data.time)


    def caculate(self, resultQueue_, file_):
        # BLANKETT K4-2015P4
        # IDENTITET 198806198795 20160426 221941
        # NAMN GANG XU
        file_.write("#BLANKETT K4-2016P4\n")
        file_.write("#IDENTITET 198806198795 20170220 135219\n")
        file_.write("#NAMN GANG XU\n")
        AmountProfit = 0.0
        AmountProfitInEur = 0.0
        processedItems = 0
        self.constructTimeSeriseVector()

        rateDataList = {"": ""}

        for timedData in self.timedSeriseVector:
            ticketData = self.ticketDataDict[timedData.ticketNumber]
            try:
                if ticketData.type == TicketData.TicketType.CREDIT \
                        or ticketData.type == TicketData.TicketType.BALANCE \
                        or ticketData.type == TicketData.TicketType.SELL_LIMIT \
                        or ticketData.type == TicketData.TicketType.BUY_LIMIT:
                    continue

                if ticketData.profit == 0:
                    continue

                dealTime = timedData.time
                dealtype = ticketData.type
                dealSize = ticketData.size
                dealRatio = ticketData.item.currencyType.ratio
                dealPrice = 0.0
                dealPair = ticketData.item.currencyType.pair

                dealPriceInTargetAmount = 0.0
                dealPriceInSEK = 0.0

                if timedData.isOpen:
                    dealPrice = ticketData.openprice
                else:
                    dealPrice = ticketData.closeprice

                dealPriceInTargetAmount = dealSize * dealRatio * dealPrice


                if not("SEK" in dealPair):
                    dealPair = dealPair[-3:] + "_SEK"

                if timedData.isOpen:

                        ticketData.openBaseRate = RateFetcher.dataAssembler(dealPair,
                                                          datetime.datetime.fromtimestamp(dealTime), rateDataList).rateBid


                dealPriceInSEK = dealPriceInTargetAmount * ticketData.openBaseRate
                ticketData.targetValue = dealPriceInTargetAmount
                ticketData.targetName = dealPair[:3]

                if ticketData.swap != 0:
                    eurToSEK = RateFetcher.dataAssembler("EUR_SEK",
                                                         datetime.datetime.fromtimestamp(dealTime), rateDataList).rateBid
                    ticketData.swapInSek = ticketData.swap * eurToSEK

                buyValueInSEK = 0.0
                sellValueInSEK = 0.0
                win = 0.0
                lost = 0.0
                if timedData.isOpen:
                    ticketData.openpriceInSek = dealPriceInSEK
                else:
                    ticketData.closepriceInSek = dealPriceInSEK
                    if dealtype == TicketData.TicketType.SELL:
                        ticketData.profitInSek = ticketData.openpriceInSek - ticketData.closepriceInSek + ticketData.swapInSek
                        buyValueInSEK = ticketData.closepriceInSek
                        sellValueInSEK = ticketData.openpriceInSek + ticketData.swapInSek
                    else:
                        ticketData.profitInSek = ticketData.closepriceInSek - ticketData.openpriceInSek + ticketData.swapInSek
                        buyValueInSEK = ticketData.openpriceInSek
                        sellValueInSEK = ticketData.closepriceInSek + ticketData.swapInSek

                    AmountProfit = AmountProfit + ticketData.profitInSek + ticketData.swapInSek
                    AmountProfitInEur = AmountProfitInEur + ticketData.profit

                    if ticketData.profitInSek > 0:
                        win = ticketData.profitInSek
                        lost = 0
                    else:
                        win = 0
                        lost = -ticketData.profitInSek



                    #file_.write("{")
                    #file_.write("Pair: {},"
                    #            " TicketNumber: {},"
                    #            " OpenInSEK: {},"
                    #            " CloseInSEK: {},"
                    #            " ProfitInEur: {},"
                    #            " ProfitInSEK: {},"
                    #            "AmountProfit: {},"
                    #            " AmountProfitInEUR: {}".format(ticketData.originalPair, ticketData.ticketNumber,
                    #                                              ticketData.openpriceInSek,ticketData.closepriceInSek,
                    #                                                                         ticketData.profit,
                    #                                                                         ticketData.profitInSek,
                    #                                                                         AmountProfit,
                    #                                                                         AmountProfitInEur))
                    #file_.write("}\n")
                    #file_.flush()
                    # UPPGIFT 3310 7793
                    # UPPGIFT 3311 usd
                    # UPPGIFT 3312 60553
                    # UPPGIFT 3313 60240
                    currentId = (processedItems + 1)%7 + 1
                    file_.write("#UPPGIFT 33" + str(currentId) + "0 {}\n".format(int(ticketData.targetValue)) +
                                "#UPPGIFT 33" + str(currentId) + "1 {}\n".format(ticketData.targetName) +
                                "#UPPGIFT 33" + str(currentId) + "2 {}\n".format(int(buyValueInSEK)) +
                                "#UPPGIFT 33" + str(currentId) + "3 {}\n".format(int(sellValueInSEK)) +
                                "#UPPGIFT 33" + str(currentId) + "4 {}\n".format(int(win)) +
                                "#UPPGIFT 33" + str(currentId) + "5 {}\n".format(int(lost)))

                    processedItems += 1

                    if processedItems % 7 == 0:
                        resultQueue_.put("Worker {}: Processed {}/{}".format(self.num, processedItems, len(self.ticketDataDict.keys())))
                        file_.write("#BLANKETTSLUT\n")
                        file_.write("#BLANKETT K4-2016P4\n")
                        file_.write("#IDENTITET 198806198795 20170220 135219\n")
                        file_.write("#NAMN GANG XU\n")
                        #print(
                        #    "Worker {}: Processed {}/{}".format(self.num, processedItems, len(self.ticketDataDict.keys())))
                        file_.flush()
            except Exception:
                resultQueue_.put("ERROR! {}".format(ticketData.print()))
                sys.stderr.flush()
                continue
            # assert False

        resultQueue_.put("DONE Worker {}: EUR: {} SEK: {}".format(self.num, AmountProfitInEur, AmountProfit))


    def __init__(self, chunkData: dict, resultQueue_, file_, num_):
        self.ticketDataDict = chunkData
        self.num = num_
        self.caculate(resultQueue_, file_)




if __name__ == "__main__":
    yearTicketDataDict = CsvReader.loadReport(sys.argv[1])
    #sys.stderr = open(saveCsvFileTo + str(os.getpid()) + "_error.out", "w")
    #filename = saveCsvFileTo + "_Test.txt"
    #file = open(filename, "wt")
    #Runner.__call__(yearTicketDataDict, multiprocessing.Queue(), file, 1)
    #file.close()
    #exit(0)

    workThread = 50
    workTotal = workThread - 1
    resultQueue = multiprocessing.Queue()

    thunkAmount = int(len(yearTicketDataDict.keys()) / workThread)
    index = 0
    nextIndex = thunkAmount
    chunk = {"":""}
    chunk.pop("")
    works = []
    for ticketNumber in sorted(yearTicketDataDict.keys()):
        if index < nextIndex:
            chunk[ticketNumber] = yearTicketDataDict[ticketNumber]
            index += 1
            continue

        print("Processing index = {} nextIndex {} totalLen: {}".format(index, nextIndex, len(yearTicketDataDict.keys())))
        workThread -= 1
        worker = multiprocessing.Process(name="worker" + str(workThread), target=work, args=(chunk, str(workThread), resultQueue, index,))
        worker.start()
        works.append(worker)
        print("Started index = {} nextIndex {} totalLen: {}".format(index, nextIndex, len(yearTicketDataDict.keys())))
        chunk.clear()
        index = nextIndex
        nextIndex += thunkAmount

        if nextIndex >= len(yearTicketDataDict.keys()):
            nextIndex = len(yearTicketDataDict.keys())

    #The last piece of worker need to start
    print("Processing index = {} nextIndex {} totalLen: {}".format(index, nextIndex, len(yearTicketDataDict)))
    workThread -= 1
    worker = multiprocessing.Process(name="worker" + str(workThread), target=work,
                                     args=(chunk, str(workThread), resultQueue, index,))
    worker.start()
    works.append(worker)
    chunk.clear()
    print("Started index = {} nextIndex {} totalLen: {}".format(index, nextIndex, len(yearTicketDataDict)))

    TotalInEUR = 0.0
    TotalInSEK = 0.0
    pattern = re.compile("DONE Worker (\d+): EUR: ([-]{0,1}\d+).(\d+) SEK: ([-]{0,1}\d+).(\d+)", re.IGNORECASE)
    while True:
        isAlive = False
        for work in works:
            if work.is_alive():
                isAlive = True

        if not(isAlive):
            for work in works:
                work.join()

            while not(resultQueue.empty()):
                output = resultQueue.get()
                if ("DONE Worker" in output):
                    print(output)
                    m = pattern.match(output)
                    assert len(m.groups()) == 5
                    TotalInEUR += float(m.group(2))
                    TotalInSEK += float(m.group(4))

                print(output)
            break
        else:
            while not(resultQueue.empty()):
                output = resultQueue.get()
                if ("DONE Worker" in output):
                    print(output)
                    m = pattern.match(output)
                    assert len(m.groups()) == 5
                    TotalInEUR += float(m.group(2))
                    TotalInSEK += float(m.group(4))

                print(output)

        time.sleep(1)

    print("TOTAL IN EUR: {} IN SEK: {}".format(TotalInEUR, TotalInSEK))
    allString = ""
    for resultFile in range(workTotal):
        blankfile = open(saveCsvFileTo + "BLANKETTER.SRU." + str(resultFile))
        allString += blankfile.read()
        blankfile.close()

    totalBlankfile = open(saveCsvFileTo + "BLANKETTER.SRU", "wt")
    allString += "#FIL_SLUT\n"

    totalBlankfile.write(allString)
    totalBlankfile.close()



