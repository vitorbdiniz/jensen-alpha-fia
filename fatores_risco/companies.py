import pandas as pd
import numpy as np
import pandas_datareader as web
import pymysql as sql
from os.path import realpath
from datetime import date

def get_prices(verbose = False):
    results = pd.DataFrame()
    p = realpath("./data/tickers.csv")
    tickers = pd.read_csv(p)
    for i in range(len(tickers["codigo_negociacao"])):
        t = tickers["codigo_negociacao"].loc[i].replace("$", "") + ".SA"
        try:
            if verbose:
                print("Buscando preços de " + str(t))
            results.append(web.get_data_yahoo(t, "2010-12-31", date.today()))
        except:
            if verbose:
                print("Erro em "+str(t))
    return results

get_prices(True)
