from os.path import realpath
import pandas as pd
import datetime as dt
import pandas_datareader as web

import padding as pad






"""

    DICTIONARIES AND DATAFRAMES

"""

def rearange_prices(prices, start=dt.date(2010,1,1), end=dt.date.today(), column = "Adj Close"):
    return pd.DataFrame({ ticker : prices[ticker][column] for ticker in prices.keys() }, index=date_range(start, end, frequency="D"))

def kill_duplicates(df, check_column="index"):
    if check_column == "index":
        validate = list(df.index)
    else:
        validate = list(df[check_column])
    
    df["index"] = df.index.copy()
    df.index = range(0, len(df.index))

    ( duplicates, checked ) = ( set(), set() )
    for i in df.index:
        if validate[i] not in checked:
            checked.add( validate[i] )
        else:
            duplicates.add(i)
    result = df.drop(labels=duplicates, axis="index")
    result.index = result["index"]
    result = result.drop(columns="index")
    return result


"""

        PANDAS SERIES

"""

def eliminate_duplicates_indexes(serie):
    index = []
    check_indexes = set()
    values = []
    for i in serie.index:
        if i not in check_indexes:
            index += [i]
            values += [serie.loc[i]]
            check_indexes.add(i)
    return pd.Series(values, index)

def get_previous_data(series, index):
    try:
        i = series.index.get_loc(index, method="pad")
    except:
        i = 0
        
    return series.iloc[i]


"""

    TIME MANIPULATION

"""

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

def days_per_year(date_array):
    result = dict()
    for d in date_array:
        result[d.year] = result[d.year] + 1 if d.year in result else 1
    return result


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

def date_range(start, end, frequency="D"):
    
    start = dt.datetime(start.year, start.month, start.day)
    end = dt.datetime(end.year, end.month, end.day)
    if frequency == "D":
       result = pd.DatetimeIndex([start + dt.timedelta(days=i) for i in range( (end-start).days+1 )])
    elif frequency == "Y":
       result = pd.DatetimeIndex([ dt.date(i, 1, 1) for i in range( start.year, end.year+1 )])
    
    else:
        raise AttributeError("'frequency'")
    return result

def getQuarterRange(start=dt.date.today(), end=dt.date.today()):
    '''
        Retorna trimestres existentes em um dado intervalo de datas
        Ex.: getQuarterRange("2019-11-01", "2020-12-20") -> ["4T2019","1T2020","2T2020","3T2020","4T2020"]
    '''

    firstQ = getQuarter(start)
    lastQ = getQuarter(end)
    res = []
    for y in range(get_year(start), get_year(end)+1):
        for q in range(1, 5):
            quarter = str(q)+"T"+str(y)
            if compareQuarters(quarter, firstQ) >= 0 and compareQuarters(quarter, lastQ) <= 0:
                res.append(quarter)
    return res


def getUtilDays(start, end, form="date"):
    '''
        Busca dias úteis em um intervalo dado
    '''
    selic = getSelic(start, end)
    util = list(selic.index)
    if form == "str":
        util = [str(x) for x in util]
    return util


def dateReformat(date, toUsual=True, form="date"):
    if toUsual:
        d = str(date).split('-')[::-1]
        d = d[0] + "/" + d[1] + "/" + d[2]
    else:
        d = str(date).split("/")[::-1]
        if form == "str":
            d = d[0] + "-" + d[1] + "-" + d[2]
        elif form == "date":
            d = dt.date(int(d[0]), int(d[1]), int(d[2]))
    return d

def datesReformat(dates, toUsual=True, form="date"):
    res = [dateReformat(date, toUsual, form=form) for date in dates]
    return res


def getYears(start, end):
    s = int(start[0:4])
    e = int(end[0:4])
    return [i for i in range(s, e+1)]




def transform(date, freq):
    if freq == "quarterly":
        result = getQuarter(str(date))
    elif freq == "annually":
        result = get_year(str(date))
    else:
        result = date
    return result

def get_month(date):
    '''
        retorna o mês de uma data

        Ex.: get_month("2005-01-05") -> 1
    '''
    return int(date[5:7])

def get_day(date):
    '''
        retorna o dia de uma data

        Ex.: get_day("2005-01-05") -> 5
    '''
    return int(date[8:10])

def get_year(date):
    '''
        retorna o ano de uma data

        Ex.: get_year("2005-01-05") -> 2005
    '''
    return int(date[0:4])    

def str_to_date(string):
    return dt.date(year=get_year(string), month=get_month(string), day=get_day(string))

def list_str_to_list_dates(str_list):
    return [str_to_date(s) for s in list(str_list)]


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
        index = getUtilDays(start, end)
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


"""

    RETURNS

"""

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
        if r == None or pd.isna(r):
            acumulado += [capital-1]
        else:
            capital = capital*(1+r)
            acumulado += [capital-1]
    return acumulado

def avg_return(retornos):

    acc_return = cumulative_return(retornos=retornos)[-1]
    periods = len(retornos) if len(retornos) % 2 == 1 or acc_return > 0 else len(retornos)-1
    avg = (1+acc_return)**(1/periods)-1
    return avg

def mean_annual_return(array):
    cosmos = cumulative_return(array)
    daily_return_cosmos = (cosmos[-1]+1)**(1/len(cosmos))-1
    annual_return_cosmos = (daily_return_cosmos+1)**(250)-1
    return annual_return_cosmos    


"""

    OUTROS CÁLCULOS

"""

def getSelic(start = dt.date.today(), end = dt.date.today(), verbose = 0, persist = False):
    pad.verbose("Buscando série histórica da Selic", level=5, verbose=verbose)
    start = dateReformat(str(start))
    end = dateReformat(str(end))

    url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ str(start) +"&dataFinal="+str(end)

    start = dateReformat(str(start), toUsual=False, form="date")
    end = dateReformat(str(end), toUsual=False, form="date")

    try:
        selic = pd.read_csv(url, sep=";")
    except:
        selic = pd.DataFrame()

    if "valor" in selic.columns:
        selic["valor"] = [ x/100 for x in reformatDecimalPoint(selic["valor"], to=".")]
        selic.index = datesReformat(selic["data"], False)
        selic = pd.DataFrame({"valor":list(selic["valor"])}, index = selic.index)
    else:
        selic = pd.read_csv("./data/selic.csv", index_col=0)
        selic.index = [dt.date(year=int(d[0:4]), month=int(d[5:7]), day=int(d[8:10])) for d in selic.index]
        selic = selic.loc[start:end]

    selic.index = pd.DatetimeIndex(selic.index)

    if persist:
        selic.to_csv("./data/selic.csv")
    pad.verbose("line", level=5, verbose=verbose)
    return selic




def total_liquidity_per_year(volume, date_array = None, form = "dic", year_form="int"):
    if date_array == None:
        date_array = days_per_year(volume.index)
    result = dict()
    for d in volume.index:
        if pd.isna(volume.loc[d]):
            volume.loc[d] = 0
        result[d.year] = result[d.year] + volume.loc[d] if d.year in result else volume.loc[d]
    
    if year_form == "datetime":
        result = { dt.datetime(year=x, month=1, day=1) : result[x] for x in result.keys() }

    if form == "Series":
        result = pd.Series( [result[x] for x in result.keys()] , index = result.keys())
        

    return result


def mean_liquidity_per_year(volume, date_array = None):
    result = total_liquidity_per_year(volume, date_array)
    result = {year : result[year]/date_array[year]   if year in result else 0   for year in date_array}
    return result

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


def write_file(path, data):
    #path = realpath(path)
    f = open(path, "w")
    f.write(data) 
    f.close()
    return




def trailing_sum(array, period = 12):
    return [ sum(array[0:i]) for i in range(period)] + [sum(array[i-period:i]) for i in range(period, len(array))]

