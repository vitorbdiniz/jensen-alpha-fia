import datetime as dt
import pandas as pd
import numpy as np
import statistics as st
from scipy.stats import zscore

import busca_dados
import matrixDB
import util
import padding as pad


"""

    CÁLCULO DE INDICADORES PARA CARTEIRA DE TAMANHO

"""

def get_all_book_to_market(prices, dates, tickers, verbose=0):
    """
        Computa os indicadores book-to-market (BM ou PVPA) de vários ativos para vários períodos

        Retorna um DataFrame com os BMs para cada ativo(coluna) em um instante de tempo (linha)

        NEFIN:
            The High Minus Low Factor (HML) is the return of a portfolio long on stocks with high
            book-to-market ratio (“High”) and short on stocks with low book-to-market ratio (“Low”).

            Every January of year t, we (ascending) sort the eligible stocks into 3 quantiles
            (portfolios) according to the book-to-market ratio of the firms in June of year t-1. Then,
            we compute the equal-weighted returns of the first portfolio (“Low”) and the third
            portfolio (“High”). The HML Factor is the return of the “High” portfolio minus the return
            of the “Low” portfolio.

    """
    patrimonio_liquido = matrixDB.get_equity(environment="prod", verbose=verbose)
    patrimonio_liquido["VPA"] = [x if x != 0 else None for x in patrimonio_liquido["VPA"]]

    patrimonio_liquido = rearange_BMs(patrimonio_liquido, dates)

    pad.verbose("- Calculando os Valores de Mercado -", level=2, verbose=verbose)
    tickers = set(patrimonio_liquido.keys())
    BM = dict()
    for ticker in prices:
        if ticker in tickers:
            BM[ticker] = get_company_BMs(prices[ticker], patrimonio_liquido[ticker], dates, ticker, verbose=verbose) 

    BM = pd.DataFrame(BM, index = dates)
    return BM
    
def get_company_BMs(prices, VPA, dates, ticker, verbose=0):
    pad.verbose(f"Calculando Book-to-Market de {ticker}", level=5, verbose=verbose)

    VPA = VPA.dropna()
    if len(VPA) == 0:
        VPA = pd.Series([0 for x in dates],index=dates)
    prices = prices.dropna()
    BMs = pd.Series([],index=[])

    for d in dates:
        price = util.get_previous_data(prices, dt.datetime(year=d.year, month=6, day=30))
        valor_VPA = util.get_previous_data(VPA, dt.datetime(year=d.year, month=6, day=30))
        if valor_VPA == 0:
            BM = pd.Series([None], index=[d])    
        else:
            BM = pd.Series([price / float(valor_VPA)], index=[d])
        BMs = BMs.append(BM)
    return BMs

def rearange_BMs(patrimonio_liquido, dates):
    patrimonio_liquido = patrimonio_liquido[["codigo_negociacao", "release_date", "VPA"]]
    aux = dict()

    for i in range(patrimonio_liquido.shape[0]):    
        ticker = patrimonio_liquido["codigo_negociacao"].iloc[i]
        date = patrimonio_liquido["release_date"].iloc[i]
        total = patrimonio_liquido["VPA"].iloc[i]
        total = pd.Series([total], [date])

        if ticker not in aux:
            aux[ticker] = total
        elif date not in aux[ticker].index:
            aux[ticker] = aux[ticker].append(total)

    result = pd.DataFrame(aux, index = util.date_range(start=dates[0], end = dt.date.today()))

    result.dropna(inplace=True, how='all')
    return result
