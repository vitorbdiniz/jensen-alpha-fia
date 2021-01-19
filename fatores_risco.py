import busca_dados
import datetime as dt
import pandas as pd
import util

def calcula_fatores_risco(prices, carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")

    fatores = pd.DataFrame(index=carteiras["value"].index)
    returns = util.allReturns(prices)

    fatores["fator_mercado"]  = marketFactor(Rm="^BVSP", Rf = "selic", start=start, end=end, verbose=verbose)
    fatores["fator_tamanho"]  = calculate_factor(carteiras["size"], returns, factor_name="tamanho", nome_carteira1="small", nome_carteira2="big",  verbose=verbose)
    fatores["fator_valor"]    = calculate_factor(carteiras["value"], returns, factor_name="valor", nome_carteira1="high", nome_carteira2="low",  verbose=verbose)
    fatores["fator_liquidez"] = calculate_factor(carteiras["liquidity"], returns, factor_name="liquidez", nome_carteira1="iliquid", nome_carteira2="liquid",  verbose=verbose)
    fatores["fator_momentum"] = calculate_factor(carteiras["momentum"], returns, factor_name="momentum", nome_carteira1="winner", nome_carteira2="loser",  verbose=verbose)
    #fatores["QMJ"] = calculate_factor(carteiras["quality"], returns, factor_name="qualidade", nome_carteira1="junk", nome_carteira2="quality",  verbose=verbose)
    #fatores["fator_beta"] = calculate_factor(carteiras["beta"], returns, factor_name="beta", nome_carteira1="low_beta", nome_carteira2="high_beta",  verbose=verbose)

    return fatores

def marketFactor(Rm = "^BVSP", Rf = "selic",start = str(dt.date.today()), end=str(dt.date.today()), verbose=False):   

    if verbose:
        print("Calculando fator de risco de mercado")

    ibov = busca_dados.get_prices(Rm, start, end, verbose=False)["^BVSP"]
    Rm = util.getReturns(ibov)
    Rf = busca_dados.getSelic(start, end)

    mkt = []
    dates = []
    i = 1
    for date in Rm.index:
        if verbose:
            print(str(i)+". Calculando fator mercado para o periodo " + str(date) + " ---- restam "+str(len(Rm.index)-i))
            i += 1
        if date in Rf.index:
            mkt.append(Rm["returns"].loc[date]- Rf["valor"].loc[date])
            dates.append(date)
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return pd.Series(mkt, index=dates)

def calculate_factor(carteiras, returns, factor_name, nome_carteira1, nome_carteira2,  verbose=False):
    if verbose:
        print("Calculando fator " + factor_name)
    factor = []
    dates = []
    i=1
    for i in range(1,len(carteiras.index)):
        period = str(carteiras.index[i-1])
        now = str(carteiras.index[i])
        if verbose:
            print(str(i)+". Calculando fator "+ factor_name +" para o periodo " + str(period) + " ---- restam "+str(len(carteiras.index)-i))
            i += 1
        ret = [0,0] #[big, small] or [liquid, iliquid] ...
        n = [0,0]#[big, small] ...
        for ticker in carteiras.columns:
            if period in list(returns[ticker].index):
                if carteiras[ticker].loc[period] == nome_carteira1:
                    n[1] += 1
                    ret[1] += returns[ticker]["returns"].loc[period]
                elif carteiras[ticker].loc[period] == nome_carteira2:
                    n[0] += 1 if returns[ticker]["returns"].loc[period] != None else 0
                    ret[0] += returns[ticker]["returns"].loc[period] if returns[ticker]["returns"].loc[period] != None else 0
        if n[1] == 0:
            ret[1],n[1] = 0,1
        if n[0] == 0:
            ret[0],n[0] = 0,1
        factor.append(ret[1]/n[1] - ret[0]/n[0])
        dates.append(now)
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    pd.DataFrame(factor, index=dates).to_csv("./data/fatores/"+factor_name+".csv")
    return pd.Series(factor, index=dates)
