import csv
import TicketData
import os
import datetime
import time
import io


def loadReport(filename_: str) -> dict:
    ticketDataDict = {"": ""}
    csvfile = open(filename_, "rt")
    reader = csv.reader(csvfile)

    rownum = 0
    itemType = []
    for row in reader:
        # Save header
        if rownum == 0:
            row[5] = "Open Price"
            row[9] = "Close Price"
            header = row
        else:
            ticketData = TicketData.TicketData()
            colnum = 0
            for col in row:
                if col != "":
                    ticketData.updateValue(header[colnum], col)
                colnum += 1
                ticketDataDict[ticketData.ticketNumber] = ticketData

        rownum += 1

    csvfile.close()
    ticketDataDict.pop("")
    return ticketDataDict

