#Python libs
import datetime as dt
import pandas as pd
import pandas_datareader as web

#Workspace libs
import matrixDB
import util



def get_prices(tickers, start=dt.date.today(), end=dt.date.today(),verbose = False, get_from="yahoo", freq="daily"):
    '''
        Busca cotações de uma lista de ativos para um determinado intervalo de tempo

        Se tickers == lista de ações, então get_prices retorna as cotações dessa lista,
        senão, se tickers == "all", então o BD é acessado e todas as cotações são buscadas
    '''
    if tickers == "all":
        tickers = [ x.replace("$", "") for x in list(matrixDB.get_tickers(environment = "prod", verbose = verbose)[3])]
        tickers = kill_units(tickers)
    elif str(tickers).lower() == "ibov" or str(tickers) == "^BVSP":
        tickers = ["^BVSP"]
    elif type(tickers) != type([]):
        raise AttributeError("ticker deve ser 'all' ou list")

    if get_from=="influx":
        prices = get_prices_from_influx(tickers, start, end, verbose)
    else:
        prices = get_prices_from_yahoo(tickers, start, end, verbose, freq)
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return prices

def kill_units(tickers):
    return [t for t in tickers if len(t) == 5]

def get_last_date(prices, start):
    return prices["PETR4"]["Date"].iloc[-1] if "PETR4" in prices.keys() else start

def get_prices_from_yahoo(tickers, start, end, verbose, freq):
    prices = dict()
    i=1
    for t in tickers:
        if verbose:
            print(str(i) + ". Buscando preços de " + str(t) + " ---- faltam " + str(len(tickers)-i))
            i+=1
        try:
            if t[0] != '^':
                prices[t] = web.get_data_yahoo(t+".SA", start, end)
            else:
                prices[t] = web.get_data_yahoo(t, start, end)
            prices[t] = resample_prices(prices[t], freq)
        except:
            if verbose:
                print("------- Ação não encontrada")
    return prices

def resample_prices(prices, freq):

    liquid_days = [1 if prices["Volume"].loc[date] > 0 else 0   for date in prices.index]
    prices["liquid_days"] = liquid_days

    volume = prices["Volume"].resample(freq[0].upper()).sum()
    liquid_days = prices["liquid_days"].resample(freq[0].upper()).sum()

    prices_result = prices.resample(freq[0].upper()).pad()

    prices_result["Volume"] = volume
    prices_result["liquid_days"] = liquid_days
    prices_result.index = [str(x.date()) for x in list(prices_result.index)]

    return prices_result


def get_prices_from_influx(tickers, start, end, verbose):
    """
        Busca cotações do Influx 
    """
    stockid = pd.read_csv("./data/stocks_id.csv")
    stockid = stockid[["Id","InternalSymbol"]]
    influx = pd.read_csv("./data/precos_influx.csv")
    influx = influx[["stockid", "time","Open", "High", "Low", "Close", "Volume"]]
    influx["Date"] = [ x[0:10] for x in influx["time"]]
    prices = dict()

    i = 1
    for ticker in tickers:
        if verbose:
            print(str(i) + ". Buscando preços de " + str(ticker) + " ---- faltam " + str(len(tickers)-i))
            i+=1
        id = get_stockid(stockid, ticker)
        data = {"Date":[],"Open":[], "High":[], "Low":[], "Close":[], "Volume":[], "Adj Close":[]}
        found = False
        j = 0
        while j < influx.shape[0]:
            if influx["stockid"].iloc[j] == id:
                found = True
                data["Date"].append(influx["Date"].iloc[j])
                data["Open"].append(influx["Open"].iloc[j])
                data["High"].append(influx["High"].iloc[j])
                data["Low"].append(influx["Low"].iloc[j])
                data["Close"].append(influx["Close"].iloc[j])
                data["Adj Close"].append(influx["Close"].iloc[j])
                data["Volume"].append(influx["Volume"].iloc[j])
            elif found:
                j = influx.shape[0]
            j+=1
        prices[ticker] = pd.DataFrame(data, index=data["Date"]).drop(columns="Date")

    return prices

def get_stockid(stockid, ticker):
    for i in range(len(stockid["InternalSymbol"])):
        if stockid["InternalSymbol"].iloc[i] == ticker:
            return stockid["Id"].iloc[i]
    return -1

def getSelic(start = dt.date.today(), end = dt.date.today(), verbose = False, persist = False):
    if verbose:
        print("Buscando série histórica da Selic")
    start = util.dateReformat(start)
    end = util.dateReformat(end)
    url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ start +"&dataFinal="+end
    try:
        selicBCB = pd.read_csv(url, sep=";")
        if persist:
            selicBCB.to_csv("./data/selic.csv", sep=";")
    except:
        selicBCB = pd.read_csv("./data/selic.csv", sep=";")
    selicBCB["valor"] = [ x/100 for x in util.reformatDecimalPoint(selicBCB["valor"], to=".")]
    selicBCB["data"] = util.datesReformat(selicBCB["data"], False)
    selic = pd.DataFrame({"valor":list(selicBCB["valor"])}, index = selicBCB["data"])

    if persist:
        selic.to_csv("./data/selic.csv")
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return selic


