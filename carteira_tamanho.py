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

def get_market_caps(prices, dates, tickers, verbose=0):
    """
        Computa os valores de mercado de vários ativos para vários períodos

        Retorna um DataFrame com os valores de mercado para cada ativo(coluna) em um instante de tempo (linha)
    """
    stocks = matrixDB.get_stocks_quantity(environment="prod", verbose=verbose)
    stocks = totalstocks(stocks, dates)

    pad.verbose("- Calculando os Valores de Mercado -", level=2, verbose=verbose)
    tickers = set(stocks.keys())
    market_cap = dict()
    for ticker in prices:
        if ticker in tickers:
            market_cap[ticker] = get_company_market_caps(prices[ticker], stocks[ticker], dates, ticker, verbose=verbose) 

    market_cap = pd.DataFrame(market_cap, index = dates)            
    return market_cap

def get_company_market_caps(prices, stocks, dates, ticker, verbose=0):
    pad.verbose(f"Calculando Market Cap de {ticker}", level=5, verbose=verbose)

    stocks = stocks.dropna()
    prices = prices.dropna()
    market_caps = pd.Series([],index=[])

    for d in dates:
        price = util.get_previous_data(prices, d)
        n_stocks = util.get_previous_data(stocks, d)
        market_cap = pd.Series([price * n_stocks], index=[d])
        market_caps = market_caps.append(market_cap)

    return market_caps


def totalstocks(stocks, dates):
    stocks = stocks[["codigo_negociacao", "release_date", "totais"]]
    aux = dict()

    for i in range(stocks.shape[0]):    
        ticker = stocks["codigo_negociacao"].iloc[i]
        date = stocks["release_date"].iloc[i]
        total = stocks["totais"].iloc[i]
        total = pd.Series([total], [date])

        if ticker not in aux:
            aux[ticker] = total
        elif date not in aux[ticker].index:
            aux[ticker] = aux[ticker].append(total)

    result = pd.DataFrame(aux, index = util.date_range(start=dates[0], end = dt.date.today()))

    result.dropna(inplace=True, how='all')
    return result