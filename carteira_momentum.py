import datetime as dt
import pandas as pd

import util
import padding as pad



def get_momentum(prices, dates, tickers, verbose=0):
    """
        Computa os valores de liquidez de vários ativos para vários períodos

        Retorna um DataFrame com os valores de liquidez para cada ativo(coluna) em um instante de tempo (linha)
    """    
    
    pad.verbose("- Calculando as rentabilidades -", level=2, verbose=verbose)
    
    price_per_year = lambda prices : pd.Series({dt.datetime(d.year, 1, 1) : prices.loc[d] for d in prices.index if pd.notna(prices.loc[d])})
    price_per_period = lambda prices, period : prices.dropna().resample(str(period[0]).upper()).pad()
    increment_list = lambda iterable, factor : [ x + factor for x in iterable ]

    tickers = set(prices.keys())
    momentum = dict()
    for ticker in prices:
        if ticker in tickers:
            pad.verbose(f"Calculando as rentabilidades de {ticker}", level=5, verbose=verbose)
            #annual_prices = price_per_year(prices[ticker])
            monthly_prices = price_per_period(prices[ticker], "M")
            monthly_prices.index = increment_list(monthly_prices.index, dt.timedelta(days=1))
            momentum[ticker] = util.getReturns(monthly_prices, form="Series")
    momentum = pd.DataFrame(momentum, index = dates)
    return momentum

