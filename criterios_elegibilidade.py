import pandas as pd
import datetime as dt
import numpy as np

import util
import padding as pad

def criterios_elegibilidade(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily", liquidez_min = 0, criterion = 0.8,media_periodo = 1,persist=False, verbose = False):

    liquidez_minima = criterio_liquidez_minima(prices, start, end, freq, liquidez_min, criterion, media_periodo, verbose)
    pad.verbose("line", level=5, verbose=verbose)

    maior_liquidez = criterio_maior_liquidez(prices, start, end, freq, verbose)
    pad.verbose("line", level=5, verbose=verbose)
    
    listagem = criterio_listagem(prices, start, end, freq, verbose)
    pad.verbose("line", level=5, verbose=verbose)

    criterios = intersecao_criterios(liquidez_minima, maior_liquidez, listagem, verbose)
    if persist:
        liquidez_minima.to_csv("./data/criterios/criterio_liquidez_minima.csv")
        maior_liquidez.to_csv("./data/criterios/criterio_maior_liquidez.csv")
        listagem.to_csv("./data/criterios/criterio_listagem.csv")

    return criterios


def intersecao_criterios(liquidez_minima, maior_liquidez, listagem, verbose=False):
    intersecao_criterios = pd.DataFrame(index=listagem.index)

    pad.verbose("Calculando interseção de critérios", level=3, verbose=verbose)

    i = 1
    for col in listagem.columns:
        aux = []
        pad.verbose(str(i)+". Calculando interseção de critérios de "+ col + " ---- faltam "+str(len(listagem.columns)-i), level=5, verbose=verbose)
        i+=1
        for index in liquidez_minima.index:
            aux.append(liquidez_minima[col].loc[index] and maior_liquidez[col].loc[index] and listagem[col].loc[index])
        intersecao_criterios[col] = aux
    return intersecao_criterios


def criterio_liquidez_minima(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily", liquidez_min = 0, criterion = 0.8,media_periodo = 1, verbose = False):
    index, days_number = util.get_frequency(start, end, freq)
    pad.verbose("Aplicação do critério de liquidez mínima", level=3, verbose=verbose)


    eleitos = {q: [] for q in index}
    i = 1
    for ticker in prices.keys():
        pad.verbose(str(i) + ". Aplicando critério de liquidez mínima em " + ticker + " ---- faltam " + str(len(prices.keys())-i), level=5, verbose=verbose)
        i+=1
        for q in prices[ticker].index:
            if q in eleitos.keys() and prices[ticker]["liquid_days"].loc[q] >= criterion:
                eleitos[q] += [ticker]
    
    return elegibility_dataframe_by_dic(prices, eleitos, index)
    
def elegibility_dataframe(calculo_elegibilidade_df, dic, index):
    df = pd.DataFrame(index=index)
    for ticker in calculo_elegibilidade_df:
        aux = []
        for q in list(calculo_elegibilidade_df.index):
            if q in dic and ticker in dic[q]:
                aux += [True]
            else:
                aux += [False]
        df[ticker] = aux
    return df


def criterio_maior_liquidez(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily",verbose = False):
    pad.verbose("Aplicando o critério do ticker de maior liquidez", level=3, verbose=verbose)
    index, days_number = util.get_frequency(start, end, freq)
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
    criterion2 = elegibility_dataframe_by_dic(prices, elegibilidade_tickers, index)
    return criterion2

def getMostLiquidTicker(prices, tickers, period):
    liquidity = {}

    for t in tickers:
        liq = prices[t]["Volume"].loc[period] if period in prices[t].index else 0
        liquidity[t] = liq
    highest = list(liquidity.keys())[0]
    for t in liquidity:
        if liquidity[highest] < liquidity[t]:
            highest = t
    return highest


def criterio_listagem(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily",verbose = False):
    pad.verbose("Aplicando critério de listagem", level=3, verbose=verbose)
    index, days_number = util.get_frequency(start, end, freq)
    elegibilidade_listagem = {q:[] for q in index}
    i = 1
    for ticker in prices:
        pad.verbose(str(i)+". Aplicando critério de listagem em "+ ticker + " ---- faltam "+str(len(prices)-i), level=5, verbose=verbose)
        i += 1
        if type(prices[ticker].index[0]) == type(' '):
            q = util.transform(prices[ticker].index[0], freq)   
        else:
            q = util.transform(str(prices[ticker].index[0].date()), freq)
        if freq == "quarterly" or freq == "annually":
            q = util.getNextPeriod(q, freq)
        for t in index:
            if util.compareTime(q, t, freq) <= 0:
                elegibilidade_listagem[t].append(ticker)
    eleitos = elegibility_dataframe_by_dic(prices, elegibilidade_listagem, index)
    return eleitos


def elegibility_dataframe_by_dic(prices, dic, index):
    df = pd.DataFrame(index=index)

    for ticker in prices.keys():
        aux = []
        for q in dic.keys():
            if ticker in dic[q]:
                aux += [True]
            else:
                aux += [False]
        df[ticker] = aux
    return df