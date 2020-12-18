import datetime as dt
import pandas as pd
import pandas_datareader as web

import matrixDB



def get_prices(tickers, start=dt.date.today(), end=dt.date.today(), verbose = False):
    '''
        Busca cotações de uma lista de ativos para um determinado intervalo de tempo

        Se tickers == lista de ações, então get_prices retorna as cotações dessa lista,
        senão, se tickers == "all", então o BD é acessado e todas as cotações são buscadas
    '''
    if tickers == "all":
        tickers = matrixDB.get_tickers(environment = "prod", verbose = verbose)
        
    i = 1
    prices = dict()
    for t in tickers:
        if verbose:
            print(str(i) + ". Buscando preços de " + t + " ---- faltam " + str(len(tickers)-i))
            i+=1
        try:
            prices[t] = web.get_data_yahoo(t+".SA", start, end)
        except:
            if verbose:
                print("------- 404 -> Not found")
    return prices