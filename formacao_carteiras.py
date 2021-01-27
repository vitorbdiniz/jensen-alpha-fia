import datetime as dt
import pandas as pd
import numpy as np
import statistics as st
from scipy.stats import zscore

import busca_dados
import matrixDB
import util
import padding as pad

def forma_carteiras(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):

    BAB       = carteiraBeta(prices, amostra_aprovada, quantile, start, end, years = 3, verbose=verbose)
    size      = carteiraSize(prices, amostra_aprovada, quantile, start, end, freq,verbose)
    value     = carteiraValue(prices, amostra_aprovada, quantile, start, end, freq, verbose)
    liquidity = carteiraLiquidity(prices, amostra_aprovada, quantile, verbose)
    momentum  = carteiraMomentum(prices, amostra_aprovada, quantile, start, end, verbose)
    #quality   = carteiraQuality(prices, amostra_aprovada, start, end, verbose)

    carteiras = consolidaCarteiras(value, size, liquidity, momentum, BAB, dfUnico=False, verbose=verbose)
    return carteiras

def carteiraValue(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "high" ou "low" de acordo com o múltiplo book-to-market (BM)
    '''
    pad.verbose("Montando carteiras de valor", level=3, verbose=verbose)

    i = 1
    patrimonio_liquido = matrixDB.get_equity(environment="prod", verbose=verbose)
    value = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    for period in amostra_aprovada.index:
        pad.verbose(str(i)+". Montando carteiras de valor para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i), level=5, verbose=verbose)

        i += 1
        BM = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[period]:
                VPA = float(getVPA(patrimonio_liquido, ticker, period, freq))
                if VPA == 0:
                    BM.append(0)
                else:
                    BM.append( float(prices[ticker]["Adj Close"].loc[period]) / VPA )
            else:
                BM.append(0)
        value.loc[period] = classificar(BM, quantile, "high", "low")

    pad.verbose('line', level=3, verbose=verbose)

    return value


def carteiraSize(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), freq = "daily",verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "big" ou "small" de acordo com o seu valor de mercado
    '''
    pad.verbose("Montando carteiras de tamanho", level=3, verbose=verbose)

    stocks = matrixDB.get_stocks_quantity(environment="prod", verbose=verbose)
    i = 1
    size = pd.DataFrame(index=amostra_aprovada.index, columns = amostra_aprovada.columns)
    for period in amostra_aprovada.index:
        pad.verbose(str(i)+". Montando carteiras de tamanho para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i), level=5, verbose=verbose)
        i += 1
        market_cap = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[period]:
                N = float(totalstocks(stocks, ticker, period, freq))
                if N == 0:
                    market_cap.append(0)
                else:
                    market_cap.append( float(prices[ticker]["Adj Close"].loc[period]) * N )
            else:
                market_cap.append(0)
        size.loc[period] = classificar(market_cap, quantile, "big", "small")

    pad.verbose('line', level=3, verbose=verbose)

    return size

def carteiraLiquidity(prices, amostra_aprovada, quantile, verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "liquid" ou "iliquid" de acordo com a sua liquidez
    '''
    pad.verbose("Montando carteiras de liquidez", level=3, verbose=verbose)

    liquidity = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    i=1
    for periodo in amostra_aprovada.index:
        pad.verbose(str(i)+". Montando carteiras de liquidez para o período " + str(periodo) + " ---- restam " + str(len(amostra_aprovada.index)-i), level=5, verbose=verbose)
        i += 1
        
        liquidez_periodo = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[periodo]:
                liquidez_periodo.append(prices[ticker]["Volume"].loc[periodo])
            else:
                liquidez_periodo.append(0)
        liquidity.loc[periodo] = classificar(liquidez_periodo, quantile, "liquid", "iliquid")

    pad.verbose('line', level=3, verbose=verbose)

    return liquidity


    
def carteiraMomentum(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "winner" ou "loser" de acordo com seu retorno
    '''
    pad.verbose("Montando carteiras de momentum", level=3, verbose=verbose)
    pad.verbose("Calculando rentabilidades necessárias", level=4, verbose=verbose)

    returns = util.allReturns(prices)
    momentum = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    i = 1
    for periodo in amostra_aprovada.index:
        pad.verbose(str(i)+". Montando carteiras de momentum para o período " + str(periodo) + " ---- restam " + str(len(amostra_aprovada.index)-i), level=5, verbose=verbose)
        i += 1

        rentabilidade_periodo = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[periodo]:
                rentabilidade_periodo.append(returns[ticker]["returns"].loc[periodo])
            else:
                rentabilidade_periodo.append(0)
        momentum.loc[periodo] = classificar(rentabilidade_periodo, quantile, "winner", "loser")

    pad.verbose("line", level=3, verbose=verbose)

    return momentum

def carteiraBeta(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), years = 3, verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "high_beta" ou "low_beta" de acordo com o beta
    '''
    pad.verbose("Montando carteiras de beta", level=3, verbose=verbose)

    betas = getBeta(prices, amostra_aprovada,start, end, verbose)
    betas.to_csv("./data/alphas/betas.csv")
    #betas = pd.read_csv("./data/alphas/betas.csv", index_col=0)    
    carteira_beta = pd.DataFrame(index=amostra_aprovada.index, columns=amostra_aprovada.columns)
    i = 1
    for period in amostra_aprovada.index:
        pad.verbose(str(i)+". Montando carteiras de beta para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i), level=5, verbose=verbose)
        i += 1
        
        b = []
        for ticker in amostra_aprovada.columns:
            if period in betas.index and amostra_aprovada[ticker].loc[period] and (betas[ticker].loc[period] != None and pd.notna(betas[ticker].loc[period])):
                b.append( betas[ticker].loc[period] )
            else:
                b.append(None)

        carteira_beta.loc[period] = classificar(b, quantile, "high_beta", "low_beta")

    pad.get_line()

    return carteira_beta

def getBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    pad.verbose("Calculando betas", level=3, verbose=verbose)
    pad.verbose("Calculando retornos necessários", level=4, verbose=verbose)

    ibov = util.getReturns(busca_dados.get_prices("ibov", start, end)["^BVSP"])
    
    utilDays = util.getUtilDays(start, end)
    returns = util.allReturns(prices)
    betas_result = pd.DataFrame(index=utilDays)

    i = 1
    for ticker in returns.keys():
        pad.verbose(str(i)+". Calculando beta de " + ticker + " ---- restam " + str(len(returns.keys()) - i), level=5, verbose=verbose)
        i += 1

        check_returns = validate_returns_dates(returns[ticker], ibov)
        dates = set(check_returns.index)
        betas = pd.Series()
        j = 0
        for d in utilDays:
            d = str(d)
            if j < 21 or d not in dates:
                betas.loc[d] = None
                if d in dates:
                    j+=1
                continue
            elif j < 500: #2y para 250 dias úteis:
                stock = check_returns["stock"].iloc[0:j]
                benchmark = check_returns["benchmark"].iloc[0:j]
            else:
                stock = check_returns["stock"].iloc[j-500:j]
                benchmark = check_returns["benchmark"].iloc[j-500:j]
            b = beta(Rm=benchmark, Ra=stock)
            betas.loc[d] = b
            j+=1
        betas_result[ticker] = betas
    return betas_result

def validate_returns_dates(asset, benchmark):
    result = pd.DataFrame(columns=["stock", "benchmark"])
    benchmark_dates = set(benchmark.index)
    for d in asset.index:
        if d in benchmark_dates:
            result.loc[d] = [ asset["returns"].loc[d], benchmark["returns"].loc[d] ]
    return result


def beta(Rm, Ra):
    return np.cov(Rm, Ra)[0][1]/st.variance(Rm)



'''
    FUNÇÕES AUXILIARES
'''




def consolidaCarteiras(value, size, liquidity, momentum, beta=pd.DataFrame(), quality=pd.DataFrame(), dfUnico = False, verbose = False):
    pad.verbose("Consolidação das carteiras", level=3, verbose=verbose)

    if dfUnico:
        consolidada = pd.DataFrame(index=value.index, columns=value.columns)
        i = 1

        for ticker in value.columns:
            pad.verbose(str(i) + ". Consolidando ação: " + str(ticker) + " ---- restam " + str(len(value.columns)-i), level=5, verbose=verbose)
            i+=1
            
            col = []
            for index in value.index:
                col.append(str(value[ticker].loc[index]) +","+ str(size[ticker].loc[index]) +","+ str(liquidity[ticker].loc[index]) +","+ str(momentum[ticker].loc[index]))
            consolidada[ticker] = col
    else:
        consolidada = dict()
        i = 1
        consolidada["value"]     = value
        consolidada["size"]      = size
        consolidada["liquidity"] = liquidity
        consolidada["momentum"]  = momentum
        #consolidada["quality"]   = quality
        #consolidada["beta"]      = beta
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return consolidada

def classificar(lista, q, acima, abaixo):
    """

        0 < q <= 0.5
    """
    aux = [x for x in lista if (x != 0 and x != None)]
    if aux == []:
        return [None for i in lista]   
    inf = np.quantile(aux, q)
    sup = np.quantile(aux, 1-q)
    result = []
    for each in lista:
        if each != None and each != 0 and each > sup:
            result.append(acima)
        elif each != None and each != 0 and each < inf:
            result.append(abaixo)
        else:
            result.append(None)
    return result

'''

    INDICADORES

'''

def getVPA(PL, ticker, period, freq):
    df = PL[PL[0]==ticker]
    if df.shape[0] == 0:
        return 0
    row = 0
    for i in range(len(df[5])):
        if util.compareTime(str(period), str(df[5].iloc[i]), freq) >= 1:
            row = i
        else:
            break
    return float(df[10].iloc[row])

def totalstocks(stocks, ticker, period, freq):
    df = stocks[stocks[0]==ticker]
    if df.shape[0] == 0:
        return 0
    row = 0
    for i in range(len(df[2])):
        if util.compareTime(str(period), str(df[2].iloc[i]), freq) >= 1:
            row = i
        else:
            break
    return float(df[4].iloc[row])


