import datetime as dt
import pandas as pd
import numpy as np
import statistics as st

def forma_carteiras(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    liquidity = carteiraLiquidity(prices, amostra_aprovada, verbose)
    liquidity.to_csv("./data/liquidity.csv")
    
    value     = carteiraValue(prices, amostra_aprovada, start, end, verbose)
    value.to_csv("./data/value.csv")
    
    size      = carteiraSize(prices, amostra_aprovada, start, end, verbose)
    size.to_csv("./data/size.csv")

    momentum  = carteiraMomentum(prices, amostra_aprovada, start, end, verbose)
    momentum.to_csv("./data/momentum.csv")
    
    quality   = carteiraQuality(prices, amostra_aprovada, start, end, verbose)
    quality.to_csv("./data/quality.csv")
    
    beta      = carteiraBeta(prices, amostra_aprovada, start, end, verbose)   
    beta.to_csv("./data/beta.csv")
    
    carteiras = consolidaCarteiras(value, size, liquidity, momentum, quality, beta, True, verbose)
    carteiras.to_csv("./data/carteiras.csv")
    
    return carteiras




def carteiraValue(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "high" ou "low" de acordo com o múltiplo book-to-market (BM)
    '''

    value = pd.DataFrame(index=amostra_aprovada)
    patrimonio_liquido = 




    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return value

def carteiraSize(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "big" ou "small" de acordo com o seu valor de mercado
    '''

    #TODO
    return

def carteiraLiquidity(prices, amostra_aprovada, verbose=False):
    '''
        Classifica cada ativo por período em "liquid" ou "iliquid" de acordo com a sua liquidez
    '''
    liquidity = pd.DataFrame(index=amostra_aprovada.index)
    for periodo in amostra_aprovada.index:
        liquidez_periodo = []
        for ticker in amostra_aprovada.columns:
            if amostra_aprovada[ticker].loc[periodo]:
                liquidez_periodo.append(prices[ticker]["Volume"].loc[periodo])
        liquidity.loc[periodo] = classificar(liquidez_periodo, "liquid", "iliquid")

    return liquidity


    
def carteiraMomentum(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "winner" ou "loser" de acordo com seu retorno
    '''
    
    #TODO
    return




def carteiraQuality(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
    '''

    #TODO
    return

def carteiraBeta(prices, amostra_aprovada, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período em "high_beta" ou "low_beta" de acordo com o beta
    '''


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
    return [acima if each >= med else abaixo   for each in lista]