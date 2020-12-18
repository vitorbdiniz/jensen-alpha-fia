import busca_dados
import datetime as dt
import pandas as pd
import util

def calcula_fatores_risco(prices, carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    MKT = marketFactor(Rm="^BVSP", Rf = "selic", start=start, end=end, verbose=verbose)
    
    fatores = pd.DataFrame(index=MKT.index)

    fatores["MKT"] = MKT
    fatores["SMB"] = sizeFactor(carteiras, start, end, verbose)
    fatores["HML"] = valueFactor(carteiras, start, end, verbose)
    fatores["LIQ"] = liquidityFactor(carteiras, start, end, verbose)
    fatores["MOM"] = momentumFactor(carteiras, start, end, verbose)
    fatores["QMJ"] = qualityFactor(carteiras, start, end, verbose)
    fatores["BAB"] = betaFactor(carteiras, start, end, verbose)

    return fatores

def marketFactor(Rm = "^BVSP", Rf = "selic",start = str(dt.date.today()), end=str(dt.date.today()), verbose=False):  
    ibov = busca_dados.get_prices([Rm], start, end, verbose)["^BVSP"]
    Rm = util.getReturns(ibov)

    if Rf == "selic":
        Rf  = busca_dados.getSelic(start, end, verbose)
    if verbose:
        print("Calculando fator de risco de mercado")
    mkt = []
    dates = []
    for date in Rm.index:
        date = str(date.date())
        if date in Rf.index:
            mkt.append(Rm["returns"].loc[date]- Rf["valor"].loc[date])
            dates.append(date)
    return pd.DataFrame({"MKT":mkt}, index=dates)



def sizeFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return 
def valueFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return
def liquidityFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return
def momentumFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return
def qualityFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return
def betaFactor(carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    #TODO
    return





