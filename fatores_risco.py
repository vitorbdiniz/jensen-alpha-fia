import busca_dados
import datetime as dt
import pandas as pd
import util

def calcula_fatores_risco(prices, carteiras, start= str(dt.date.today()), end= str(dt.date.today()), persist = False, verbose=False):
    fatores = pd.DataFrame(index=carteiras["value"].index)
    returns = util.allReturns(prices)

    fatores["fator_mercado"]  = marketFactor(Rm="^BVSP", Rf = "selic", start=start, end=end, persist=persist, verbose=verbose)
    fatores["fator_tamanho"]  = calculate_factor(carteiras["size"], returns, factor_name="tamanho", nome_carteira1="small", nome_carteira2="big", persist=persist, verbose=verbose)
    fatores["fator_valor"]    = calculate_factor(carteiras["value"], returns, factor_name="valor", nome_carteira1="low", nome_carteira2="high", persist=persist, verbose=verbose)
    fatores["fator_liquidez"] = calculate_factor(carteiras["liquidity"], returns, factor_name="liquidez", nome_carteira1="iliquid", nome_carteira2="liquid", persist=persist, verbose=verbose)
    fatores["fator_momentum"] = calculate_factor(carteiras["momentum"], returns, factor_name="momentum", nome_carteira1="loser", nome_carteira2="winner", persist=persist, verbose=verbose)
    #fatores["QMJ"] = calculate_factor(carteiras["quality"], returns, factor_name="qualidade", nome_carteira1="junk", nome_carteira2="quality", persist=persist, verbose=verbose)
    #fatores["BAB"] = calculate_factor(carteiras["beta"], returns, factor_name="beta", nome_carteira1="low_beta", nome_carteira2="high_beta", persist=persist, verbose=verbose)

    return fatores

def marketFactor(Rm = "^BVSP", Rf = "selic",start = str(dt.date.today()), end=str(dt.date.today()), persist = False, verbose=False):  
    if verbose:
        print("Calculando fator mercado") 
    ibov = busca_dados.get_prices(Rm, start, end, verbose)["^BVSP"]
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
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return pd.Series(mkt, index=dates)

def calculate_factor(carteiras, returns, factor_name, nome_carteira1, nome_carteira2, persist=False, verbose=False):
    if verbose:
        print("Calculando fator " + factor_name)
    factor = []
    dates = []
    for period in carteiras.index:
        returns = [0,0] #[big, small] or [liquid, iliquid] ...
        n = [0,0]#[big, small] ...
        for ticker in carteiras.columns:
            if period in returns.index:
                if carteiras[ticker].loc[period] == nome_carteira1:
                    n[1] += 1
                    returns[1] += returns[ticker]["returns"].loc[period]
                elif carteiras[ticker].loc[period] == nome_carteira2:
                    n[0] += 1
                    returns[0] += returns[ticker]["returns"].loc[period]
        factor.append(returns[1]/n[1] - returns[0]/n[0])
        dates.append(period)
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    
    return pd.Series(factor, index=dates)
