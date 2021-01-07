import pandas as pd
import datetime as dt
import numpy as np

import util


def criterios_elegibilidade(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily", liquidez_min = 0, criterion = 0.8,media_periodo = 1,verbose = False):
    liquidez_minima = criterio_liquidez_minima(prices, start, end, freq, liquidez_min, criterion, media_periodo, verbose)
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    maior_liquidez = criterio_maior_liquidez(prices, start, end, freq, verbose)
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    listagem = criterio_listagem(prices, start, end, freq, verbose)
    if verbose:
        print("-------------------------------------------------------------------------------------------")

    intersecao_criterios = pd.DataFrame(index=listagem.index)

    i = 1
    for col in listagem.columns:
        aux = []
        if verbose:
            print(str(i)+". Calculando interseção de critérios de "+ col + " ---- faltam "+str(len(prices)-i))
            i+=1
        for index in liquidez_minima.index:
            aux.append(liquidez_minima[col].loc[index] and maior_liquidez[col].loc[index] and listagem[col].loc[index])
        intersecao_criterios[col] = aux
    return intersecao_criterios


def criterio_liquidez_minima(prices, start = dt.date.today(), end = dt.date.today(), freq = "daily", liquidez_min = 0, criterion = 0.8,media_periodo = 1, verbose = False):
    index, days_number = util.get_frequency(start, end, freq)
    elegibilidade_liquidez = calcula_liquidez(prices, index, start, end, days_number, freq, liquidez_min, media_periodo,verbose)
    criterion1 = aplica_criterio_liquidez(prices, elegibilidade_liquidez, index, criterion, verbose)
    return criterion1

def calcula_liquidez(prices, index, start, end, days_number, freq, liquidez_min = 0, media_periodo = 1,verbose = False):
    elegibilidade_liquidez = pd.DataFrame(index=index)
    elegibilidade_liquidez["days_number"] = days_number
    #print("liquidez minima")
    ##liquidez_min = busca_liquidez_minima(prices, liquidez_min, start, end, freq)
    #print("liquidez minima OK")
    i = 1
    for ticker in prices:
        days = {q:0 for q in index}
        if verbose:
            print(str(i) + ". Calculando dias de liquidez de " + ticker + " ---- faltam " + str(len(prices.keys())-i))
            i+=1

        #prices[ticker]["Volume"] = util.moving_average(prices[ticker]["Volume"], media_periodo)
        #print("Média Móvel OK")
        for d in prices[ticker].index:
            if prices[ticker]["Volume"].loc[d] >= liquidez_min:#.loc[d]:
                if type(d) == type(" "):
                    time = util.transform(d, freq)
                else:
                    time = util.transform(str(d.date()), freq)
                if time in list(days.keys()):
                    days[time] += 1 
        elegibilidade_liquidez[ticker] = [j for j in days.values()]
    return elegibilidade_liquidez

def busca_liquidez_minima(prices, liquidez_min, start, end, freq):
    result = []
    time, days_number = util.get_frequency(start, end, freq)
    for t in time:
        liq = []
        for ticker in prices.keys():
            if (t in prices[ticker].index):
                if (not pd.isna(prices[ticker]["Volume"].loc[t])):
                    if (prices[ticker]["Volume"].loc[t] > 0):
                        liq += [ prices[ticker]["Volume"].loc[t] ]
        if liq != []:
            result.append( np.quantile(liq, liquidez_min) )
        else:
            result.append( 0 )
    return pd.Series(result, index=time)

def aplica_criterio_liquidez(prices, elegibilidade_liquidez, index, criterion, verbose = False):
    eleitos = {q: [] for q in index}
    i = 1
    for ticker in elegibilidade_liquidez:
        if ticker == "days_number":
            continue
        if verbose:
            print(str(i) + ". Aplicando critério de liquidez mínima em " + ticker + " ---- faltam " + str(len(prices.keys())-i))
            i+=1
        for q in elegibilidade_liquidez.index:
            if elegibilidade_liquidez[ticker].loc[q]/elegibilidade_liquidez["days_number"].loc[q] >= criterion:
                eleitos[q] += [ticker]
    
    return elegibility_dataframe(elegibilidade_liquidez, eleitos, index)
    
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
    index, days_number = util.get_frequency(start, end, freq)
    elegibilidade_tickers = {q:[] for q in index}
    done = set()
    i = 1
    for ticker in prices:
        if ticker in done:
            continue
        print(str(i)+". Aplicando critério de ticker de maior liquidez em "+ ticker + " ---- faltam "+str(len(prices)-i))
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
    index, days_number = util.get_frequency(start, end, freq)
    elegibilidade_listagem = {q:[] for q in index}
    i = 1
    for ticker in prices:
        if verbose:
            print(str(i)+". Aplicando critério de listagem em "+ ticker + " ---- faltam "+str(len(prices)-i))
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