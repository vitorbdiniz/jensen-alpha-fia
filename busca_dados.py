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
    
    return prices

def kill_units(tickers):
    return [t for t in tickers if len(t) == 5]

def get_prices_from_yahoo(tickers, start, end, verbose):
    prices = dict()
    i=1
    for t in tickers:
        t = t.upper()
        pad.verbose(f"{i}. Buscando preços de {t} ---- faltam {len(tickers)-i}", level=5, verbose=verbose)
        i+=1
        
        try:
            ticker = t if t[0] == '^' else str(t+".SA")
            p = web.get_data_yahoo(ticker, start, end)
            p["Close"] = p["Adj Close"]
            prices[t] = p
        except:
            pad.verbose("----> Ação não encontrada", level=5, verbose=verbose)
    return prices




def get_prices_from_influx(tickers, start, end, verbose):
    """
        Busca cotações do Stocks, base de dados no BD Influx do TC 
    """
    data = get_prices_data(verbose=verbose)

    prices = dict()

    i = 1
    for ticker in tickers:
        pad.verbose(f"{i}. Buscando preços de {ticker} ---- faltam {len(tickers)-i}", level=5, verbose=verbose)
        i+=1

        df = data[data['ticker'] == ticker].copy()
        if df.shape[0] > 0:
            df.index = pd.DatetimeIndex(df['time'])
            df.drop(columns=['ticker', 'time'], inplace=True)
            df = util.drop_duplicate_index(df)
            prices[ticker] = df
        else:
            pad.verbose("-> Ação não encontrada", level=5, verbose=verbose)
    return prices

    
def get_dict_id_ticker(id_to_ticker = True, verbose=0):
    """
        Cria um dicionário que mapeia o Id para o ticker do ativo se id_to_ticker == True;
        Cria um dicionário que mapeia o ticker para o Id do ativo se id_to_ticker == False.

        Retorna ponteiro para o dicionário dict() criado
    """
    pad.verbose(f"Criando dicionário para id_to_ticker = {id_to_ticker}", level=3, verbose=verbose)

    stocks_id = pd.read_csv("./data/stocks_id.csv")[["Id", "InternalSymbol"]]

    if id_to_ticker:
        dictionary = { stocks_id["Id"].iloc[row] : stocks_id["InternalSymbol"].iloc[row] for row in range(stocks_id.shape[0])}
    else:
        dictionary = { stocks_id["InternalSymbol"].iloc[row] : stocks_id["Id"].iloc[row] for row in range(stocks_id.shape[0])}
    return dictionary

def get_prices_data(dictionary = None, verbose=0):
    if not dictionary:
        dictionary = get_dict_id_ticker(verbose=verbose)
    pad.verbose(f"Buscando dados de cotações", level=3, verbose=verbose)

    data = pd.read_csv("./data/precos_influx.csv")
    data = data[["stockid", "time","Open", "High", "Low", "Close", "financialvolume"]]
    
    pad.verbose(f"Pré-processando dados de cotações", level=3, verbose=verbose)
    data["time"] = [str_to_datetime(data["time"].iloc[i], datatype='date') for i in range(data.shape[0])]
    data["ticker"] = [ dictionary[id] for id in data["stockid"]] 

    data = data.drop(columns=['stockid']).rename(columns={"financialvolume":"Volume"})
    return data

def str_to_datetime(string, datatype = 'datetime'):
    result = dt.datetime.strptime(str(string), '%Y-%m-%dT%H:%M:%SZ')   
    if datatype == 'date' or datatype == dt.date:
        result = dt.date(year=result.year, month=result.month, day=result.day)
    return result
