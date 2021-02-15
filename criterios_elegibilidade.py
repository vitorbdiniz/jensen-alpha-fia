import pandas as pd
import datetime as dt
import numpy as np

import util
import padding as pad

def criterios_elegibilidade(prices, start = dt.date.today(), end = dt.date.today(), liquidez_min = 0, criterion = 0.8, verbose = 0):
    index = util.get_frequency(start, end)[0]

    liquidez_minima = criterio_liquidez_minima(prices, index, start, end, liquidez_min, criterion, verbose)
    pad.verbose("line", level=5, verbose=verbose)

    maior_liquidez = criterio_maior_liquidez(prices, index, start, end, verbose)
    pad.verbose("line", level=5, verbose=verbose)
    
    listagem = criterio_listagem(prices, index, start, end, verbose)
    pad.verbose("line", level=5, verbose=verbose)

    criterios = intersecao_criterios(liquidez_minima, maior_liquidez, listagem, verbose)

    return criterios


def criterio_liquidez_minima(prices, index, start = dt.date.today(), end = dt.date.today(), liquidez_min = 0, criterion = 0.8, verbose = 0):    
    pad.verbose("- Aplicação do critério de liquidez mínima -", level=3, verbose=verbose)

    eleitos = {q: [] for q in index}
    days = set(index)
    i = 1

    for ticker in prices.keys():
        pad.verbose(str(i) + ". Aplicando critério de liquidez mínima em " + ticker + " ---- faltam " + str(len(prices.keys())-i), level=5, verbose=verbose)
        i+=1
        for q in prices[ticker].index:
            if q in days and prices[ticker]["liquid_days"].loc[q] >= criterion and prices[ticker]["Volume"].loc[q] > liquidez_min:
                eleitos[q] += [ticker]
    
    return elegibility_dataframe(prices, eleitos)
    



def criterio_maior_liquidez(prices, index, start = dt.date.today(), end = dt.date.today(), verbose = False):
    pad.verbose("- Aplicando o critério do ticker de maior liquidez -", level=3, verbose=verbose)
    elegibilidade_tickers = {q:[] for q in index}
    done = set()
    i = 1
    for ticker in prices:
        if ticker in done:
            continue
        pad.verbose(str(i)+". Aplicando critério de ticker de maior liquidez em "+ ticker + " ---- faltam "+str(len(prices)-i), level=5, verbose=verbose)
        cia_tickers = util.findSimilar(ticker, list(prices.keys()))
        i+=len(cia_tickers)
        for q in elegibilidade_tickers:
            if len(cia_tickers) == 1:
                elegibilidade_tickers[q] += [ticker]
            else:
                elegibilidade_tickers[q] += [getMostLiquidTicker(prices, cia_tickers, q)]
        done = done.union({t for t in cia_tickers})   
    criterion2 = elegibility_dataframe(prices, elegibilidade_tickers)
    return criterion2

def getMostLiquidTicker(prices, tickers, period):
    liquidity = {t : prices[t]["Volume"].loc[period]*prices[t]["liquid_days"].loc[period] if period in prices[t].index else 0   for t in tickers}
    highest = list(liquidity.keys())[0]
    for t in liquidity:
        if liquidity[highest] < liquidity[t]:
            highest = t
    return highest


def criterio_listagem(prices, index, start = dt.date.today(), end = dt.date.today(), freq = "daily",verbose = 0):
    pad.verbose("- Aplicando critério de listagem -", level=3, verbose=verbose)

    elegibilidade_listagem = {q:[] for q in index}
    i = 1
    for ticker in prices:
        pad.verbose(str(i)+". Aplicando critério de listagem em "+ ticker + " ---- faltam "+str(len(prices)-i), level=5, verbose=verbose)
        i += 1
        for t in index:
            if prices[ticker].index[0] <= t :
                elegibilidade_listagem[t].append(ticker)
    criterio3 = elegibility_dataframe(prices, elegibilidade_listagem)
    return criterio3


def intersecao_criterios(liquidez_minima, maior_liquidez, listagem, verbose=0):
    pad.verbose("Calculando interseção de critérios", level=3, verbose=verbose)
    result = pd.DataFrame()

    i = 1
    for col in listagem.columns:
        pad.verbose(str(i)+". Calculando interseção de critérios de "+ col + " ---- faltam "+str(len(listagem.columns)-i), level=5, verbose=verbose)
        i+=1

        aux = [ liquidez_minima[col].loc[index] and maior_liquidez[col].loc[index] and listagem[col].loc[index]  for index in liquidez_minima.index ]
        result[col] = pd.Series(aux, index=listagem.index)

    return result


"""
    FUNÇÕES AUXILIARES
"""


def elegibility_dataframe(prices, dic):
    df = pd.DataFrame()

    for ticker in prices.keys():
        aux = [True if ticker in dic[q] else False for q in dic.keys() ]
        df[ticker] = pd.Series(aux, index=list(dic.keys()))
    return df

