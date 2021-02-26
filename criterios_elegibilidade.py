import pandas as pd
import datetime as dt
import numpy as np

import util
import padding as pad

def criterios_elegibilidade(prices, start = dt.date.today(), end = dt.date.today(), liquidez_min = 500000, criterion = 0.8, frequency = "Y", verbose = 0):
    """
        Verifica se os ativos estão de acordo com os critérios de elegibilidade propostos pelo Nefin
        http://nefin.com.br/methodology.html

        Retorna DataFrame com valor True se o ativo passar nos critérios de elegibilidade para aquele dia, False caso contrário
    """
    index = util.date_range(start, end, frequency=frequency)

    liquidez_minima = criterio_liquidez_minima(prices, index, start, end, liquidez_min, criterion, verbose)
    pad.verbose("line", level=5, verbose=verbose)    

    maior_liquidez = criterio_maior_liquidez(prices, index, start, end, verbose)
    pad.verbose("line", level=5, verbose=verbose)


    listagem = criterio_listagem(prices, index, start, end, verbose)
    pad.verbose("line", level=5, verbose=verbose)
    
    criterios = intersecao_criterios(liquidez_minima, maior_liquidez, listagem, verbose)
    
    liquidez_minima.to_csv("./data/criterios/criterio_liquidez_minima.csv")
    listagem.to_csv("./data/criterios/criterio_listagem.csv")
    maior_liquidez.to_csv("./data/criterios/criterio_maior_liquidez.csv")
    
    return criterios


def criterio_liquidez_minima(prices, index, start = dt.date.today(), end = dt.date.today(), liquidez_min = 500000, criterion = 0.8, verbose = 0):    
    """
            The stock was traded in more than 80% of the days in year t-1 with volume
        greater than R$ 500.000,00 per day. In case the stock was listed in year t-1, the
        period considered goes from the listing day to the last day of the year;
    """

    pad.verbose("- Aplicação do critério de liquidez mínima -", level=3, verbose=verbose)

    aprovados = {q.year: set() for q in index}
    set_index = set(aprovados.keys())
    util_days = 250
    i = 1

    for ticker in prices.keys():
        pad.verbose(str(i) + ". Aplicando critério de liquidez mínima em " + ticker + " ---- faltam " + str(len(prices.keys())-i), level=5, verbose=verbose)
        i+=1
        days = util.days_per_year(prices[ticker].index)
        mean_liq = util.mean_liquidity_per_year(prices[ticker]["Volume"], days)
        for q in prices[ticker].index:
            if (q.year-1 in set_index and q.year-1 in days) and (days[q.year-1] >= criterion * util_days and mean_liq[q.year-1] >= liquidez_min):
                aprovados[q.year].add(ticker)
    return elegibility_dataframe(prices, aprovados)
    

        
def criterio_maior_liquidez(prices, index, start = dt.date.today(), end = dt.date.today(), verbose = False):
    """
        The stock is the most traded stock of the firm (the one with the highest traded volume during last year);
    """
    pad.verbose("- Aplicando o critério do ticker de maior liquidez -", level=3, verbose=verbose)

    aprovados = {q.year: set() for q in index}

    done = set()
    i = 1
    for ticker in prices:
        if ticker in done:
            continue
        pad.verbose(str(i)+". Aplicando critério de ticker de maior liquidez em "+ ticker + " ---- faltam "+str(len(prices)-i), level=5, verbose=verbose)

        cia_tickers = util.findSimilar(ticker, list(prices.keys()))
        i+=len(cia_tickers)

        if len(cia_tickers) > 1:
            volumes = { cia : util.total_liquidity_per_year(prices[cia]["Volume"], date_array = None) for cia in cia_tickers }
            most_liq = getMostLiquidTicker(volumes)
            
        for q in aprovados:
            if len(cia_tickers) == 1:
                aprovados[q].add(ticker)
            elif q-1 in most_liq:
                aprovados[q].add(most_liq[q-1])
        done = done.union({t for t in cia_tickers})   
    
    return elegibility_dataframe(prices, aprovados)

def getMostLiquidTicker(volumes_per_year = dict()):
    most_liq = dict()
    highest_liq_year = dict()

    for ticker in volumes_per_year.keys():
        for y in volumes_per_year[ticker].keys():
            if y not in most_liq or volumes_per_year[ticker][y] > highest_liq_year[y]:
                most_liq[y] = ticker
                highest_liq_year[y] = volumes_per_year[ticker][y]

    return most_liq

def criterio_listagem(prices, index, start = dt.date.today(), end = dt.date.today(), verbose = 0):
    """
        The stock was initially listed prior to December of year t-1

    """
    pad.verbose("- Aplicando critério de listagem -", level=3, verbose=verbose)

    aprovados = {q.year:set() for q in index}
    i = 1
    for ticker in prices:
        pad.verbose(str(i)+". Aplicando critério de listagem em "+ ticker + " ---- faltam "+str(len(prices)-i), level=5, verbose=verbose)
        i += 1
        for i in range(prices[ticker].index[0].year+1, list(aprovados.keys())[-1]+1 ):
            aprovados[i].add(ticker)

    return elegibility_dataframe(prices, aprovados)


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
    if type(list(dic.keys())[0]) == int:
        index = pd.DatetimeIndex([dt.date(int(y), 1, 1) for y in dic.keys()])
    else:
        index = dic.keys()

    for ticker in prices.keys():
        aux = [True if ticker in dic[q] else False for q in dic.keys() ]
        df[ticker] = pd.Series(aux, index=index)
    return df

