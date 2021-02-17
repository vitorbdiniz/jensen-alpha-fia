#Python libs
import datetime as dt
import pandas as pd
import pandas_datareader as web

#Workspace libs
import matrixDB
import util
import padding as pad



def get_prices(tickers, start=dt.date.today(), end=dt.date.today(),verbose = 0, get_from="yahoo"):
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
        raise AttributeError("ticker deve ser 'all', 'ibov', '^BVSP' ou list")

    if get_from=="influx":
        prices = get_prices_from_influx(tickers, start, end, verbose)
    else:
        prices = get_prices_from_yahoo(tickers, start, end, verbose)
    
    pad.verbose("line", level=4, verbose=verbose)

    return prices

def kill_units(tickers):
    return [t for t in tickers if len(t) == 5]

def get_prices_from_yahoo(tickers, start, end, verbose):
    prices = dict()
    i=1
    for t in tickers:
        pad.verbose(str(i) + ". Buscando preços de " + str(t) + " ---- faltam " + str(len(tickers)-i), level=5, verbose=verbose)
        i+=1

        try:
            ticker = t if t[0] == '^' else str(t+".SA").upper()
            prices[t] = web.get_data_yahoo(ticker, start, end)
            prices[t].index = [x.date() for x in list(prices[t].index)]
            #prices[t] = apply_frequency(prices[t], freq)
        except:
            if verbose:
                print("------- Ação não encontrada")
    return prices



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

def getSelic(start = dt.date.today(), end = dt.date.today(), verbose = 0, persist = False):
    pad.verbose("Buscando série histórica da Selic", level=5, verbose=verbose)
    start = util.dateReformat(str(start))
    end = util.dateReformat(str(end))
    url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ start +"&dataFinal="+end

    selic = pd.read_csv(url, sep=";")
    
    if "valor" in selic.columns:
        selic["valor"] = [ x/100 for x in util.reformatDecimalPoint(selic["valor"], to=".")]
        selic.index = util.datesReformat(selic["data"], False)
        selic = pd.DataFrame({"valor":list(selic["valor"])}, index = selic.index)
    else:
        Warning("Servidor não retornou taxa Selic. Utilizando dados antigos.")
        selic = pd.read_csv("./data/selic.csv", sep=";")

    if persist:
        selic.to_csv("./data/selic.csv")
    pad.verbose("line", level=5, verbose=verbose)
    return selic
