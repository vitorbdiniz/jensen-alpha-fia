import pandas as pd
import datetime as dt
import pandas_datareader as web


def getQuarter(date):
    '''
        Converte string de data para formato trimestral.

        Ex.: getQuarter("2020-05-22") -> "2T2020"
        Ex.: getQuarter("2001-11-09T00:12:45Z") -> "4T2001"
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
    '''
        Compara 2 trimestres.

        Ex.: compareQuarters("2T2020", "1T2020") -> 1
        Ex.: compareQuarters("1T2001", "4T2000") -> -1
    '''

    firstQ = q1.split("T")
    lastQ = q2.split("T")
    return 4*(int(firstQ[1]) - int(lastQ[1])) + (int(firstQ[0]) - int(lastQ[0]))

def compareTime(t1, t2, freq):
    if freq == "quarterly":
        res = compareQuarters(t1, t2)
    elif freq == "annually":
        res = t1-t2
    elif freq == "daily" or "monthly":
        res = (dt.date(int(t1[0:4]), int(t1[5:7]), int(t1[8:10])) - dt.date(int(t2[0:4]), int(t2[5:7]), int(t2[8:10]))).days
    else:
        raise AttributeError("Frequência não estipulada corretamente")
    return res

def getNextPeriod(time, freq):
    if freq == "quarterly":
        res = nextQuarter(time)
    elif freq == "annually":
        res = int(time)+1
    elif freq == "daily":
        res = str(dt.date(int(time[0:4]), int(time[5:7]), int(time[8:10]))+ dt.timedelta(days=1))
    else:
        raise AttributeError("Frequência não estipulada corretamente")
    return res

def getYear(str_date):
    '''
        retorna o ano de uma data

        Ex.: getYear("2005-01-05") -> 2005
    '''
    return int(str_date[0:4])


def getQuarterRange(start=dt.date.today(), end=dt.date.today()):
    '''
        Retorna trimestres existentes em um dado intervalo de datas
        Ex.: getQuarterRange("2019-11-01", "2020-12-20") -> ["4T2019","1T2020","2T2020","3T2020","4T2020"]
    '''

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
    '''
        Busca dias úteis em um intervalo dado
    '''
    start = dateReformat(start)
    end = dateReformat(end)
    try:
        url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ start +"&dataFinal="+end
        selic = pd.read_csv(url, sep=";")
        util = list(datesReformat(selic["data"], toUsual=False))
    except:
        util = list(datesReformat(pd.read_csv("./data/selic.csv", sep=";")["data"], toUsual=False))
    return util


def count_quarter_days(start, end):
    '''
        Conta os dias úteis por trimestre em um intervalo [start, end]
    '''
    time = getUtilDays(start, end)
    quarters = getQuarterRange(start, end)
    qdays = {q: 0 for q in quarters}
    for t in time:
        qdays[getQuarter(t)] += 1
    return qdays


def nextQuarter(quarter):
    '''
        Retorna o trimestre que segue o trimestre fornecido

        Ex.: nextQuarter("2T2020") -> "3T2020"
    '''
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
    '''
        Conta dias úteis existentes em uma lista de datas
    '''


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

def mean_annual_return(array):
    cosmos = cumulative_return(array)
    daily_return_cosmos = (cosmos[-1]+1)**(1/len(cosmos))-1
    annual_return_cosmos = (daily_return_cosmos+1)**(250)-1
    return annual_return_cosmos    


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

def get_month(date):
    return int(date[5:7])

def get_day(date):
    return int(date[8:10])

def get_year(date):
    return int(date[0:4])    

def count_month_days(dates):
    result = []
    n = 0
    last_month = get_month(dates[0])
    for d in dates:
        if last_month == get_month(d):
            n+=1
        else:
            last_month = get_month(d)
            result.append(n)
            n = 1
    result.append(n)
    return result

def get_frequency(start = dt.date.today(), end = dt.date.today(), freq = "daily"):
    '''
        Retorna uma tupla (index, days_number), em que index representa uma lista temporal na frequência desejada e days_number, a quantidade de dias dentro de cada intervalo de tempo
        freq == "daily" or freq == "monthly" or freq == "quarterly" or freq == "annually"
    '''
    if freq == "daily":
        index = getUtilDays(str(start), str(end))
        days_number = [1 for i in index]
    elif freq =="monthly":
        index = getUtilDays(str(start), str(end))
        days_number = count_month_days(index)
        index = [dt.datetime(get_year(x), get_month(x), get_day(x)) for x in index]
        index = [ x.date().__str__() for x in pd.DataFrame(index, index=index).resample("M").pad().index]
    elif freq == "quarterly":
        index = getQuarterRange(str(start), str(end))
        days_number = [d for d in count_quarter_days(str(start), str(end)).values()]
    elif freq == "annually":
        index = getYears(str(start), str(end))
        days_number = count_year_days(getUtilDays(str(start), str(end)))
    else:
        raise AttributeError("Frequência não estipulada corretamente")
    return index, days_number

def getReturns(prices):
    r = [prices["Adj Close"].iloc[i] / prices["Adj Close"].iloc[i-1] -1 for i in range(1, len(prices.index))]
    returns = pd.DataFrame({"returns":[None]+r}, index=prices.index)
    return returns
    
def allReturns(prices = dict()):
    return {ticker:pd.DataFrame(getReturns(prices[ticker]), index=list(prices[ticker].index)) for ticker in prices.keys()}

def cumulative_return(retornos):
    capital = 1
    acumulado = []
    for r in retornos:
        capital = capital*(1+r)
        acumulado += [capital-1]
    return acumulado


def moving_average(array, period):
    '''
        Calcula a média móvel para um período selecionado.
    '''
    array = pd.Series(array) if type(array) == type([]) else array

    if period <= 1:
        return array
    MA = array.rolling(window=period).mean()
    NaN = MA[MA.isna()]
    MA = MA[MA.notna()]
    sum_acc = 0
    replaced_NaN = []
    for i in NaN.index:
        sum_acc += array.iloc[i]
        replaced_NaN += [sum_acc/(i+1)]
    NaN = pd.Series(replaced_NaN, index=NaN.index)
    return NaN.append(MA)
