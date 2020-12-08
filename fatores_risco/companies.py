import pandas as pd
import pandas_datareader as web
from os.path import realpath
from datetime import date

def get_prices(persist = True, verbose = False):
    p = realpath("../data/tickers.csv")
    tickers = pd.read_csv(p)
    results = pd.DataFrame(columns=["codigo_cvm", "ticker_id","date","High","Low","Open","Close","Volume","Adj Close"])
    for i in range(len(tickers["codigo_negociacao"])):
        t = tickers["codigo_negociacao"].loc[i].replace("$", "") + ".SA"
        if verbose:
            print(str(i+1) + ". Buscando preços de " + str(t))
        try:
            prices = web.get_data_yahoo(t, "2010-12-31", date.today())
            prices["codigo_cvm"] = [tickers["codigo_cvm"].loc[i] for x in range(len(prices["High"]))]
            prices["ticker_id"] = [tickers["ticker_id"].loc[i] for x in range(len(prices["High"]))]
            prices["date"] = prices.index
            results = results.append(prices, ignore_index=True)
        except:
            if verbose:
                print("Erro em "+str(t))
    if persist:
        results.to_csv(realpath("../data/prices.csv"))
    return results

get_prices(True, True)
