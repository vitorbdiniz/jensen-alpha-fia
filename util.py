import pandas as pd
import datetime as dt
import pandas_datareader as web


def getQuarter(date):
    '''
        Converte string de data para formato trimestral.

        Ex.: getQuarter("2020-05-22") -> "2T2020"
    '''
    d = str(date).split("-")  # d[0] == year; d[1] == month; d[2] == day
    if int(d[1]) <= 3:
        q = "1"
    elif int(d[1]) <= 6:
        q = "2"
    elif int(d[1]) <= 9:
        q = "3"
    else:
        q = "4"
    return q + "T" + d[0]


def compareQuarters(q1, q2):
    firstQ = q1.split("T")
    lastQ = q2.split("T")
    return 4*(int(firstQ[1]) - int(lastQ[1])) + (int(firstQ[0]) - int(lastQ[0]))


def getYear(str_date):
    return int(str_date[0:4])


def getQuarterRange(start='2010-01-01', end='2020-12-14'):
    firstQ = getQuarter(start)
    lastQ = getQuarter(end)
    res = []
    for y in range(getYear(start), getYear(end)+1):
        for q in range(1, 5):
            quarter = str(q)+"T"+str(y)
            if compareQuarters(quarter, firstQ) >= 0 and compareQuarters(quarter, lastQ) <= 0:
                res.append(quarter)
    return res


def getUtilDays(start, end):
    return [str(x.date()) for x in web.get_data_yahoo("^BVSP", start=start, end=end).index]


def count_quarter_days(start, end):
    time = getUtilDays(start, end)
    quarters = getQuarterRange(start, end)
    qdays = {q: 0 for q in quarters}
    for t in time:
        qdays[getQuarter(t)] += 1
    return qdays


def nextQuarter(quarter):
    q = quarter.split("T")
    nextq = 0
    nexty = 0
    if q[0] == '4':
        nextq = 1
        nexty = int(q[1]) + 1
    else:
        nextq = nexty = int(q[0])+1
        nexty = int(q[1])
    return str(nextq)+"T"+str(nexty)


def count_year_days(dates):
    res = []
    days = 0
    year = dates[0][0:4]
    for d in dates:
        if d[0:4] == year:
            days += 1
        else:
            res += [days]
            days = 1
            year = d[0:4]

    return res + [days]


def getCode(ticker):
    ind = -1
    for i in range(len(ticker)):
        if ord(ticker[i]) >= ord('0') and ord(ticker[i]) <= ord('9'):
            ind = i
            break
    return ticker[0:ind]


def findSimilar(ticker, ticker_list):
    code = getCode(ticker).upper()
    similar = []
    for t in ticker_list:
        if code == getCode(t).upper():
            similar += [t]
    return similar


def getMostLiquidTicker(prices, tickers, quarter):
    liquidity = {}

    for t in tickers:
        liq = 0
        for d in prices[t].index:
            if getQuarter(str(d)) == quarter:
                liq += prices[t]["Volume"].loc[d]
        liquidity[t] = liq
    highest = list(liquidity.keys())[0]
    for t in liquidity:
        if liquidity[highest] < liquidity[t]:
            highest = t
    return highest


def reformatDecimalPoint(commaNumberList, to="."):
    return [float(commaNumber.replace(",", to)) for commaNumber in commaNumberList]


def dateReformat(date, toUsual=True):
    if toUsual:
        d = str(date).split('-')[::-1]
        d = d[0] + "/" + d[1] + "/" + d[2]
    else:
        d = str(date).split("/")[::-1]
        d = d[0] + "-" + d[1] + "-" + d[2]
    return d


def datesReformat(dates, toUsual=True):
    res = []
    for date in dates:
        res += [dateReformat(date, toUsual)]
    return res


def getYears(start, end):
    s = int(start[0:4])
    e = int(end[0:4])
    return [i for i in range(s, e+1)]


def transform(date, freq):
    if freq == "quarterly":
        result = getQuarter(str(date))
    elif freq == "annually":
        result = getYear(str(date))
    else:
        result = date
    return result
