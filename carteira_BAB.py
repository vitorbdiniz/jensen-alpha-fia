import pandas as pd
import datetime as dt

from numpy import cov, zeros
from statistics import variance

from util import date_range
from busca_dados import get_prices
import padding as pad

def get_all_betas(prices:pd.DataFrame, start=dt.date(2010, 1, 1), end = dt.date.today(), method = "standard", verbose = 0):
    """
        Beta = corr * (stdev_i / stdev_m)
        one-year rolling standard deviation for volatilities (st_dev) and a five-year horizon for the correlation
    
        The portfolios are rebalanced every calendar month.
    """
    
    ibov:pd.Series = get_prices("ibov", start=start, end=end)["^BVSP"]["Close"]
    #ibov_stdev = ibov.rolling(window=250).std()

    index = date_range(start, end, frequency="D")
    month_index = date_range(start, end, frequency="M")
    result = pd.DataFrame({ticker : get_trailling_betas(prices[ticker], ibov, index, months=month_index,asset=ticker, window = 250, method=method, verbose=verbose) for ticker in prices.columns}, index=month_index)
    return result

def get_trailling_betas(Rp, Rm, index, months, asset=None, window = 0, method = "standard", verbose=0):
    """
        if method == "Frazzini":
            Beta = corr * (stdev_Rp / stdev_Rm)
            one-year rolling standard deviation for volatilities (st_dev) and a five-year horizon for the correlation
        elif method == "standard":
            Beta = cov(Rp,Rm) / Var(Rm)
    """
    pad.verbose(f"Calculando betas de {asset}", level=4, verbose=verbose)

    if Rp.shape[0] < window:
        return zeros(Rp.shape[0])

    df = pd.DataFrame({"asset":Rp, "market":Rm}, index=index)
    df.dropna(inplace=True)
    Beta = pd.Series([], [])

    for I in months:
        try:
            i = df.index.get_loc(I,method="pad")
        except:
            continue
        if i >= window:
            Rp = df["asset"].iloc[i-window : i]
            Rm = df["market"].iloc[i-window : i]
            Beta = Beta.append( pd.Series([beta(Rp, Rm, method=method)], index=[I]) )
        else:
            Beta = Beta.append(pd.Series([None], index=[I]))
    return Beta

def beta(Rp, Rm, method = "standard"):
    if method == "standard":
        Beta = cov(Rp, Rm)[0][1] / variance(Rm)
    elif method == "frazzini":
        Beta = Rp.corr(Rm) * Rp.std() / Rm.std()
    return Beta
