import datetime as dt
import pandas as pd
import numpy as np
import statistics as st

import busca_dados
import matrixDB
import util

def forma_carteiras(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):

    size      = carteiraSize(prices, amostra_aprovada, start, end, freq,verbose)
    value     = carteiraValue(prices, amostra_aprovada, start, end, freq, verbose)
    liquidity = carteiraLiquidity(prices, amostra_aprovada, verbose)
    momentum  = carteiraMomentum(prices, amostra_aprovada, start, end, verbose)
    #beta      = carteiraBeta(prices, amostra_aprovada, start, end, years = 3, verbose=verbose)
    beta = pd.DataFrame()
    #quality   = carteiraQuality(prices, amostra_aprovada, start, end, verbose)
    carteiras = consolidaCarteiras(value, size, liquidity, momentum, beta, dfUnico=False, verbose=verbose)
    return carteiras




def carteiraValue(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "high" ou "low" de acordo com o múltiplo book-to-market (BM)
    '''
    if verbose:
        print("Montando carteiras de valor")

    i = 1
    patrimonio_liquido = matrixDB.get_equity(environment="prod", verbose=verbose)
    value = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    for period in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de valor para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i))
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
        value.loc[period] = classificar(BM, "high", "low")

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    
    return value


def carteiraSize(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq = "daily",verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "big" ou "small" de acordo com o seu valor de mercado
    '''
    if verbose:
        print("Montando carteiras de tamanho")
    stocks = matrixDB.get_stocks_quantity(environment="prod", verbose=verbose)
    i = 1
    size = pd.DataFrame(index=amostra_aprovada.index, columns = amostra_aprovada.columns)
    for period in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de tamanho para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i))
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
        size.loc[period] = classificar(market_cap, "big", "small")

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return size

def carteiraLiquidity(prices, amostra_aprovada, verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "liquid" ou "iliquid" de acordo com a sua liquidez
    '''
    if verbose:
        print("Montando carteiras de liquidez")

    liquidity = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    i=1
    for periodo in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de liquidez para o período " + str(periodo) + " ---- restam " + str(len(amostra_aprovada.index)-i))
            i += 1
        liquidez_periodo = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[periodo]:
                liquidez_periodo.append(prices[ticker]["Volume"].loc[periodo])
            else:
                liquidez_periodo.append(0)
        liquidity.loc[periodo] = classificar(liquidez_periodo, "liquid", "iliquid")

    if verbose:
        print("-------------------------------------------------------------------------------------------")

    return liquidity


    
def carteiraMomentum(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "winner" ou "loser" de acordo com seu retorno
    '''
    if verbose:
        print("Montando carteiras de momentum")
        print("Calculando rentabilidades necessárias")

    returns = util.allReturns(prices)
    momentum = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    i = 1
    for periodo in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de momentum para o período " + str(periodo) + " ---- restam " + str(len(amostra_aprovada.index)-i))
            i += 1

        rentabilidade_periodo = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[periodo]:
                rentabilidade_periodo.append(returns[ticker]["returns"].loc[periodo])
            else:
                rentabilidade_periodo.append(0)
        momentum.loc[periodo] = classificar(rentabilidade_periodo, "winner", "loser")

    if verbose:
        print("-------------------------------------------------------------------------------------------")

    return momentum




def carteiraQuality(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
    '''

    # Profitability = z (z_gpoa + zroe + zroa + zcfoa + zgmar + zacc) 
    # Growth = z (zΔgpoa + zΔroe + zΔroa + zΔcfoa + zΔgmar)
    # Safety = z(zbab + zlev + zo + zz + zevol)
    # Quality = z (Profitabiliy + Growth + Safety)

    if verbose:
        print("Montando carteiras de qualidade")



    if verbose:
        print("-------------------------------------------------------------------------------------------")


    #TODO
    return

def carteiraBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), years = 3, verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "high_beta" ou "low_beta" de acordo com o beta
    '''

    if verbose:
        print("Montando carteiras de beta")
        print("- Calculando betas necessários")

    betas = getBeta(prices, start, end)
    carteira_beta = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    i = 1
    for period in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de beta para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i))
            i += 1
        b = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[period] and betas[ticker]:
                b.append( betas[ticker]["beta"].loc[period] )
            else:
                b.append(0)
        carteira_beta.loc[period] = classificar(betas, "high_beta", "low_beta")

    if verbose:
        print("-------------------------------------------------------------------------------------------")

    return carteira_beta

def getBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    if verbose:
        print("Calculando retornos necessários")
    ibov = util.getReturns(busca_dados.get_prices("ibov", start, end)["^BVSP"])
    
    utilDays = util.getUtilDays(start, end)

    returns = util.allReturns(prices)
    betas_result = pd.DataFrame(index=ibov.index)

    i = 1
    for ticker in returns.keys():
        if verbose:
            print(str(i)+". Calculando beta de " + ticker + " ---- restam " + str(len(returns.keys()) - i))
            i += 1
        check_returns = validate_returns_dates(returns[ticker], ibov)
        dates = set(check_returns.index)
        betas = []
        j = 0
        for d in utilDays:
            if j < 21 or d not in dates:
                betas.append(0)
                continue
            elif j < 500: #2y para 250 dias úteis:
                stock = check_returns["stock"].iloc[0:j]
                benchmark = check_returns["benchmark"].iloc[0:j]

            else:
                stock = check_returns["stock"].iloc[j-500:j]
                benchmark = check_returns["benchmark"].iloc[j-500:j]
            b = beta(Rm=benchmark, Ra=stock)
            betas.append(b)
            j+=1

        betas_result[ticker] = betas
    return betas_result

def validate_returns_dates(asset, benchmark):
    result = pd.DataFrame(columns=["stock", "benchmark"])
    benchmark_dates = set(benchmark.index)
    for d in asset.index:
        if d in benchmark_dates:
            result.loc[d] = [asset["returns"], benchmark["returns"]]
    return result


def beta(Rm, Ra):
    return np.cov(Rm, Ra)[0][1]/st.variance(Rm)



'''
    FUNÇÕES AUXILIARES
'''




def consolidaCarteiras(value, size, liquidity, momentum, beta, dfUnico = False, verbose = False):
    if verbose:
        print("Consolidação das carteiras")

    if dfUnico:
        consolidada = pd.DataFrame(index=value.index, columns=value.columns)
        i = 1

        for ticker in value.columns:
            if verbose:
                print(str(i) + ". Consolidando ação: " + str(ticker) + " ---- restam " + str(len(value.columns)-i))
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
        consolidada["beta"]      = beta
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return consolidada

def classificar(lista, acima, abaixo):
    aux = [x for x in lista if (x != 0 and x != None and x != "None")]
    if aux == []:
        lista = [0 for i in lista]
        med = 99999
    else:
        med = st.median(aux)
    result = []
    for each in lista:
        if each != None and each >= med:
            result.append(acima)
        elif each != None and each != 0:
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


