import datetime as dt
import pandas as pd

from util import total_liquidity_per_year
import padding as pad



def get_liquidities(volumes, dates, tickers, verbose=0):
    """
        Computa os valores de liquidez de vários ativos para vários períodos

        Retorna um DataFrame com os valores de liquidez para cada ativo(coluna) em um instante de tempo (linha)
    """    
    pad.verbose("- Verificando os volumes -", level=2, verbose=verbose)

    tickers = set(volumes.columns)
    get_company_liquidities = lambda volumes, ticker, verbose : [ total_liquidity_per_year(volumes, form="Series", year_form="datetime"),  pad.verbose(f"Verificando liquidez de {ticker}", level=5, verbose=verbose)][0]
    liquidities = pd.DataFrame({ ticker : get_company_liquidities(volumes[ticker], ticker, verbose)   for ticker in volumes    if ticker in tickers}, index = dates)

    return liquidities
