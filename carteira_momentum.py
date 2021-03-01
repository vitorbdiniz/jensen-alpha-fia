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

    tickers = set(prices.keys())
    momentum = dict()
    for ticker in prices:
        if ticker in tickers:
            pad.verbose(f"Calculando as rentabilidades de {ticker}", level=5, verbose=verbose)
            annual_prices = price_per_year(prices[ticker])
            momentum[ticker] = util.getReturns(annual_prices, form="Series")

    momentum = pd.DataFrame(momentum, index = dates)

    return momentum

