import datetime as dt
import pandas as pd
import numpy as np
import statistics as st
import matrixDB
import util

def forma_carteiras(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False, persist=False):

    value     = carteiraValue(prices, amostra_aprovada, start, end, freq, verbose)
    size      = carteiraSize(prices, amostra_aprovada, start, end, freq,verbose)
    liquidity = carteiraLiquidity(prices, amostra_aprovada, verbose)
#    momentum  = carteiraMomentum(prices, amostra_aprovada, start, end, verbose)
#    quality   = carteiraQuality(prices, amostra_aprovada, start, end, verbose)
#    beta      = carteiraBeta(prices, amostra_aprovada, start, end, verbose)       

#    carteiras = consolidaCarteiras(value, size, liquidity, momentum, quality, beta, True, verbose)
    

    if persist:
        liquidity.to_csv("./data/carteiras/liquidity.csv")
        value.to_csv("./data/carteiras/value.csv")
        size.to_csv("./data/carteiras/size.csv")
#        momentum.to_csv("./data/carteiras/momentum.csv")
#        quality.to_csv("./data/carteiras/quality.csv")
#        beta.to_csv("./data/carteiras/beta.csv")
#        carteiras.to_csv("./data/carteiras/carteiras.csv")
    
#    return carteiras




def carteiraValue(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq="daily", verbose=False):
    '''
        Classifica cada ativo por período em "high" ou "low" de acordo com o múltiplo book-to-market (BM)
    '''
    if verbose:
        print("Montando carteiras de valor")


    patrimonio_liquido = matrixDB.get_equity(environment="prod", verbose=verbose)
    value = pd.DataFrame(index=amostra_aprovada.index)
    for period in amostra_aprovada.index:
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

def getVPA(PL, ticker, period, freq):
    df = PL[PL[0]==ticker]
    release_date = df[5].iloc[0]
    for i in range(df[5]):
        if util.compareTime(period, df[5].iloc[i], freq) >= 1:
            release_date = df[5].iloc[i]
        else:
            break
    df = df[df[5] == release_date]
    return df[10].iloc[0]


def carteiraSize(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), freq = "daily",verbose=False):
    '''
        Classifica cada ativo por período em "big" ou "small" de acordo com o seu valor de mercado
    '''
    if verbose:
        print("Montando carteiras de tamanho")

    stocks = matrixDB.get_stocks_quantity(environment="prod", verbose=verbose)
    size = pd.DataFrame(index=amostra_aprovada.index)
    for period in amostra_aprovada.index:
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

def totalstocks(stocks, ticker, period, freq):
    df = stocks[stocks[0]==ticker]
    release_date = df[2].iloc[0]
    for i in range(df[2]):
        if util.compareTime(period, df[2].iloc[i], freq) >= 1:
            release_date = df[2].iloc[i]
        else:
            break
    df = df[df[2] == release_date]
    return df[5].iloc[0]


def carteiraLiquidity(prices, amostra_aprovada, verbose=False):
    '''
        Classifica cada ativo por período em "liquid" ou "iliquid" de acordo com a sua liquidez
    '''
    if verbose:
        print("Montando carteiras de liquidez")

    liquidity = pd.DataFrame(index=amostra_aprovada.index)
    for periodo in amostra_aprovada.index:
        liquidez_periodo = []
        print(periodo)
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



    if verbose:
        print("-------------------------------------------------------------------------------------------")


    
    #TODO
    return




def carteiraQuality(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
    '''
    if verbose:
        print("Montando carteiras de qualidade")



    if verbose:
        print("-------------------------------------------------------------------------------------------")


    #TODO
    return

def carteiraBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "high_beta" ou "low_beta" de acordo com o beta
    '''

    if verbose:
        print("Montando carteiras de beta")



    if verbose:
        print("-------------------------------------------------------------------------------------------")


    #TODO
    return

'''
    FUNÇÕES AUXILIARES
'''

def consolidaCarteiras(value, size, liquidity, momentum, quality, beta, dfUnico = False, verbose = False):
    if verbose:
        print("Consolidação das carteiras")

    if dfUnico:
        consolidada = pd.DataFrame(index=value.index)
        i = 1

        for ticker in value.columns:
            if verbose:
                print(str(i) + ". Consolidando ação: " + str(ticker) + " ---- restam " + str(len(value.columns)-i))
                i+=1
            col = []
            for index in value.index:
                col.append(str(value[ticker].loc[index]) +","+ str(size[ticker].loc[index]) +","+ str(liquidity[ticker].loc[index]) +","+ str(momentum[ticker].loc[index]) +","+ str(quality[ticker].loc[index]) +","+ str(beta[ticker].loc[index]))
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
                q += [str(quality[ticker].loc[index]) ]
                b += [str(beta[ticker].loc[index])]

            consolidada["value"] = v
            consolidada["size"] = s          
            consolidada["liquidity"] = l
            consolidada["momentum"] = m
            consolidada["quality"] = q
            consolidada["beta"] = b

    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return consolidada

def classificar(lista, acima, abaixo):
    med = st.median(lista)
    result = []
    for each in lista:
        if each >= med:
            result.append(acima)
        elif each != 0:
            result.append(abaixo)
        else:
            result.append(None)
    return result


