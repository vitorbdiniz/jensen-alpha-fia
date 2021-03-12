import datetime as dt
import pandas as pd
from statistics import mean
from sys import maxsize

from busca_dados import get_prices
from util import total_liquidity_per_year, getReturns, get_previous_data, drop_duplicate_index
import padding as pad



def get_liquidities(quotations, dates, tickers, verbose=0):
    """
        Computa os valores de liquidez de vários ativos para vários períodos

        Retorna um DataFrame com os valores de liquidez para cada ativo(coluna) em um instante de tempo (linha)
    """
    volumes = quotations["volumes"]
    prices = quotations["prices"]

    pad.verbose("- Calculando Índices de Iliquidez -", level=2, verbose=verbose)

    tickers = set(volumes.columns)
    ILLIQ = illiquidity_indexes(volumes, prices, verbose=verbose)
    
    return ILLIQ


def illiquidity_indexes(volumes:pd.DataFrame, prices:pd.DataFrame, verbose=0) -> pd.DataFrame:
    P = market_caps_ratio()
    data = {ticker : illiquidity_index(volumes[ticker], prices[ticker], P, ticker, verbose=verbose) for ticker in volumes.columns}
    Iindexes:pd.DataFrame = drop_duplicate_index(pd.DataFrame(data))
    return Iindexes



def illiquidity_index(volumes:pd.Series, prices:pd.Series, P:pd.Series, ticker:str, verbose=0) -> pd.Series:
    """
        The Illiquidity of stock i is a measure of how its stock price moves in response to the its
    traded volume. We construct this measure as in Acharya and Pedersen (2005):
    """
    pad.verbose(f"Calculando índice de iliquidez de {ticker}", level=5, verbose=verbose)
    
    volumes = volumes.fillna(0)
    prices = prices.dropna()
    P = P.dropna()

    volumes = volumes.append(pd.Series([None], index=[maxsize]))
    r = getReturns(prices, form="Series")
    month = volumes.index[0].month


    illiquid_index:pd.Series = pd.Series([],[])
    illiquid_values:list = []

    for i in volumes.index:
        if i != maxsize and month != i.month:
            avg = min(mean(illiquid_values), 30) if len(illiquid_values) > 0 else 30
            illiquid_index = illiquid_index.append(pd.Series([avg], index=[dt.datetime(i.year, i.month, 1)] ))
            month = i.month
            illiquid_values = []
        elif i == maxsize:
            avg = min(mean(illiquid_values), 30) if len(illiquid_values) > 0 else 0
            illiquid_index = illiquid_index.append(pd.Series([avg], index=[dt.datetime(volumes.index[-2].year, volumes.index[-2].month, 1)] ))
        if i != maxsize and volumes.loc[i] != 0:
            illiquid_values.append( abs(get_previous_data(r, i, dropna=True)) / ( get_previous_data(volumes, i, dropna=True) / get_previous_data(P,i, dropna=True) ) )
    return illiquid_index



def market_caps_ratio(start = dt.datetime(2000,1,31), end = dt.datetime.today()) -> pd.Series:
    """
        ratio between market capitalizations of the market portfolio at the end of
        month t-1 and at the end of January 2000.
    """

    ibov:pd.Series = get_prices("^BVSP", start, end)["^BVSP"]["Close"]
    ibov = pd.Series([x / ibov.iloc[0] for x in ibov.values], index=ibov.index).resample("M").pad()

    return ibov
