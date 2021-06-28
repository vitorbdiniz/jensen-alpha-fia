#Python libs
import datetime as dt
import pandas as pd
import pandas_datareader as web

#Workspace libs

from scripts.database import matrixDB
from scripts.util import padding as pad

def get_prices(tickers='all', start=dt.date.today(), end=dt.date.today(), verbose=0):
    '''
        Busca cotações de uma lista de ativos para um determinado intervalo de tempo

        Se tickers == lista de ações, então get_prices retorna as cotações dessa lista,
        senão, se tickers == "all", então o BD é acessado e todas as cotações são buscadas
    '''
    if tickers == "all":
        tickers = [ x.replace("$", "") for x in list(matrixDB.get_tickers(environment = "prod")[3])]
        tickers = kill_units(tickers)
    elif str(tickers).lower() == "ibov" or str(tickers) == "^BVSP":
        tickers = ["^BVSP"]
    elif type(tickers) != type([]):
        raise AttributeError("ticker deve ser 'all', 'ibov', '^BVSP' ou list")

    prices = get_prices_from_yahoo(tickers, start, end, verbose=verbose)
    
    return prices

def kill_units(tickers):
    return [t for t in tickers if len(t) == 5]

def get_prices_from_yahoo(tickers, start, end, verbose=0):
    prices = dict()
    i = 1
    for t in tickers:
        t = t.upper()
        pad.verbose(f'{i}. Buscando Preços de {t} ---- faltam {len(tickers)-i} ---- status: ', level=5, verbose=verbose, end='')
        i+=1
        try:
            ticker = t if t[0] == '^' else str(t+".SA")
            p = web.get_data_yahoo(ticker, start, end)
            prices[t] = p
            status = 'OK'
        except:
            status = 'Não encontrado'
        finally:
            pad.verbose(status, level=5, verbose=verbose)

    return prices

def str_to_datetime(string, datatype = 'datetime'):
    result = dt.datetime.strptime(str(string), '%Y-%m-%dT%H:%M:%SZ')
    if datatype == 'date' or datatype == dt.date:
        result = result.date()
    return result

def get_currency(pair = "USDBRL", start="2010-01-01", end=dt.datetime.today()):
    return web.get_data_yahoo(pair+"=X", start=start, end=end)
