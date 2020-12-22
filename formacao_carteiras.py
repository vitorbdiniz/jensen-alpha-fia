import datetime as dt
import pandas as pd
import numpy as np
import statistics as st

import busca_dados
import matrixDB
import util

def forma_carteiras(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False, persist=False):

    value     = carteiraValue(prices, amostra_aprovada, start, end, freq, verbose)
    value.to_csv("./data/carteiras/value.csv")
    size      = carteiraSize(prices, amostra_aprovada, start, end, freq,verbose)
    size.to_csv("./data/carteiras/size.csv")
    liquidity = carteiraLiquidity(prices, amostra_aprovada, verbose)
    liquidity.to_csv("./data/carteiras/liquidity.csv")
    momentum  = carteiraMomentum(prices, amostra_aprovada, start, end, verbose)
    momentum.to_csv("./data/carteiras/momentum.csv")
#    quality   = carteiraQuality(prices, amostra_aprovada, start, end, verbose)
#    beta      = carteiraBeta(prices, amostra_aprovada, start, end, years = 5, verbose=verbose)       

    carteiras = consolidaCarteiras(value, size, liquidity, momentum, dfUnico=False, verbose=verbose)
    #carteiras = consolidaCarteiras(value, size, liquidity, momentum, quality, beta, dfUnico=True, verbose=verbose)

    if persist:
        liquidity.to_csv("./data/carteiras/liquidity.csv")
        value.to_csv("./data/carteiras/value.csv")
        size.to_csv("./data/carteiras/size.csv")
        momentum.to_csv("./data/carteiras/momentum.csv")
#        quality.to_csv("./data/carteiras/quality.csv")
#        beta.to_csv("./data/carteiras/beta.csv")
    return carteiras




def carteiraValue(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):
    '''
        Classifica cada ativo por período em "high" ou "low" de acordo com o múltiplo book-to-market (BM)
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
                BM.append( prices[ticker]["Adj Close"].loc[period] / getVPA(patrimonio_liquido, ticker, period, freq) )
            else:
                BM.append(0)
        value.loc[period] = classificar(BM, "high", "low")

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    
    return value


def carteiraSize(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq = "daily",verbose=False):
    '''
        Classifica cada ativo por período em "big" ou "small" de acordo com o seu valor de mercado
    '''
    if verbose:
        print("Montando carteiras de tamanho")

    i = 1
    stocks = matrixDB.get_stocks_quantity(environment="prod", verbose=verbose)
    size = pd.DataFrame(index=amostra_aprovada.index, columns =amostra_aprovada.columns)
    for period in amostra_aprovada.index:
        if verbose:
            print(str(i)+". Montando carteiras de tamanho para o período " + str(period) + " ---- restam " + str(len(amostra_aprovada.index)-i))
            i += 1
        market_cap = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[period]:
                market_cap.append( prices[ticker]["Adj Close"].loc[period] * totalstocks(stocks, ticker, period, freq) )
            else:
                market_cap.append(0)
        size.loc[period] = classificar(market_cap, "big", "small")

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return size


def carteiraLiquidity(prices, amostra_aprovada, verbose=False):
    '''
        Classifica cada ativo por período em "liquid" ou "iliquid" de acordo com a sua liquidez
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
        Classifica cada ativo por período em "winner" ou "loser" de acordo com seu retorno
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
        Classifica cada ativo por período em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
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

def carteiraBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), years = 5, verbose=False):
    '''
        Classifica cada ativo por período em "high_beta" ou "low_beta" de acordo com o beta
    '''

    if verbose:
        print("Montando carteiras de beta")
        print("- Calculando betas necessários")

    betas = getBeta(prices, amostra_aprovada, start, end)
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
        carteira_beta.loc[period] = classificar(betas, "big", "small")

    if verbose:
        print("-------------------------------------------------------------------------------------------")

    return carteira_beta

def getBeta(prices, start= dt.date.today(), end= dt.date.today(), verbose=False):
    if verbose:
        print("Calculando retornos para o beta")
    ibov = util.getReturns(busca_dados.get_prices("ibov", start, end)["^BVSP"])
    returns = util.allReturns(prices)
    betas_result = dict()

    i = 1
    for ticker in returns.keys():
        betas = []
        equity = pd.DataFrame()
        if verbose:
            print(str(i)+". Calculando beta de " + ticker + " ---- restam " + str(len(returns.keys()) - i))
            i += 1
        for i in range(len(returns[ticker].index)):
            if i < 21:
                betas.append(0)
                continue
            if i- 21 < 500: #2y para 250 dias úteis:
                equity = returns[ticker].iloc[0:i]

            else:
                equity = returns[ticker].iloc[i-500:i]

            equity["market"] = ibov["returns"].loc[equity.index[0]:len(equity.index)]
            betas.append(beta(equity["market"], equity["returns"]))


        betas_result[ticker] = pd.DataFrame(betas, index = returns[ticker]["returns"])
    
    return betas_result



def beta(Rm, Ra):
    return np.cov(Rm, Ra)[0][1]/st.variance(Rm)



'''
    FUNÇÕES AUXILIARES
'''




def consolidaCarteiras(value, size, liquidity, momentum, dfUnico = False, verbose = False):
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

        for ticker in value.columns:
            if verbose:
                print(str(i) + ". Consolidando ação: " + str(ticker) + " ---- restam " + str(len(value.columns)-i))
                i+=1
            col = []
            v,s,l,m,q,b = [],[],[],[],[],[]
            for index in value.index:
                v += [str(value[ticker].loc[index]) ]
                s += [str(size[ticker].loc[index]) ]
                l += [str(liquidity[ticker].loc[index])]
                m += [str(momentum[ticker].loc[index]) ]
                #q += [str(quality[ticker].loc[index]) ]
                #b += [str(beta[ticker].loc[index])]

            consolidada["value"] = v
            consolidada["size"] = s          
            consolidada["liquidity"] = l
            consolidada["momentum"] = m
            #consolidada["quality"] = q
            #consolidada["beta"] = b

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return consolidada

def classificar(lista, acima, abaixo):
    aux = [x for x in lista if x != 0]
    if aux == []:
        lista = [0 for i in lista]
        med = 99999
    else:
        med = st.median(aux)
    result = []
    for each in lista:
        if each >= med:
            result.append(acima)
        elif each != 0:
            result.append(abaixo)
        else:
            result.append(None)
    return result

'''

    INDICADORES

'''

def getVPA(PL, ticker, period, freq):
    df = PL[PL[0]==ticker]
    release_date = df[5].iloc[0]
    for i in range(len(df[5])):
        if util.compareTime(period, df[5].iloc[i], freq) >= 1:
            release_date = df[5].iloc[i]
        else:
            break
    df = df[df[5] == release_date]
    return df[10].iloc[0]


def totalstocks(stocks, ticker, period, freq):
    df = stocks[stocks[0]==ticker]
    release_date = df[2].iloc[0]
    for i in range(len(df[2])):
        if util.compareTime(period, df[2].iloc[i], freq) >= 1:
            release_date = df[2].iloc[i]
        else:
            break
    df = df[df[2] == release_date]
    return df[5].iloc[0]

