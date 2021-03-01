import datetime as dt
import pandas as pd
import numpy as np
import statistics as st
from scipy.stats import zscore

import busca_dados
import matrixDB
import util
import padding as pad

from carteira_tamanho import get_market_caps
from carteira_valor import get_all_book_to_market
from carteira_liquidez import get_liquidities

from fator_qualidade import carteiraQuality 

"""

    FORMAÇÃO DE CARTEIRAS

"""

def forma_carteiras(prices, amostra_aprovada, quantile=1/3, start= dt.date.today(), end= dt.date.today(), verbose=0, persist=False):
    carteiras = dict()

    #betas = getBeta(prices, amostra_aprovada,start, end, verbose)
    #betas.to_csv("./data/alphas/betas.csv")
    #betas = pd.read_csv("./data/alphas/betas.csv", index_col=0)

    closing_prices = util.rearange_prices(prices, start, end, column = "Adj Close")
    volumes = util.rearange_prices(prices, start, end, column = "Volume")

    carteiras['size']       = monta_carteiras("tamanho", "big", "small", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    carteiras['value']      = monta_carteiras("valor", "high", "low", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    carteiras['liquidity']  = monta_carteiras("liquidez", "liquid", "iliquid", volumes, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    #carteiras['momentum']   = monta_carteiras("momentum", "winner", "loser", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    #carteiras['BAB']        = monta_carteiras("bab", "high_beta", "low_beta", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    #carteiras['quality']    = monta_carteiras("qmj", "quality", "junk", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose, persist=persist)
    
    return carteiras

"""

    FORMAÇÃO DE CADA CARTEIRA

"""
def monta_carteiras(nome_carteira, carteira_acima, carteira_abaixo, prices, amostra_aprovada, quantile, start=dt.date(2010, 1, 1), end = dt.date.today(), verbose = 0, persist=False):
    """
        Identifica a carteira que deve ser formada e busca o indicador referente a ela

        retorna um DataFrame com ativos classificados em uma carteira específica
    """
    pad.verbose(f"- Montando carteiras de {nome_carteira} -", level=2, verbose=verbose)
    if nome_carteira.lower() == "tamanho" or nome_carteira.lower() == "size" or nome_carteira.lower() == "smb":
        carteira = get_market_caps(prices=prices, dates=amostra_aprovada.index, tickers=amostra_aprovada.columns, verbose=verbose)
    
    elif nome_carteira.lower() == "valor" or nome_carteira.lower() == "value" or nome_carteira.lower() == "hml":
        carteira = get_all_book_to_market(prices=prices, dates=amostra_aprovada.index, tickers=amostra_aprovada.columns, verbose=verbose)
    
    elif nome_carteira.lower() == "liquidez" or nome_carteira.lower() == "liquidity" or nome_carteira.lower() == "iml":
        carteira = get_liquidities(volumes=prices, dates=amostra_aprovada.index, tickers=amostra_aprovada.columns, verbose=verbose)
    
    elif nome_carteira.lower() == "momento" or nome_carteira.lower() == "momentum" or nome_carteira.lower() == "mom" or nome_carteira.lower() == "wml":
        carteira = 0 #TODO
    
    elif nome_carteira.lower() == "beta" or nome_carteira.lower() == "bab" or nome_carteira.lower() == "betting against beta":
        carteira = 0 #TODO
    
    elif nome_carteira.lower() == "quality" or nome_carteira.lower() == "qmj" or nome_carteira.lower() == "qualidade":
        carteira = 0 #TODO
    
    else:
        raise ValueError(f"nome_carteira mal especificado: nome_carteira = {nome_carteira}")

    carteira = classificador_df(carteira, amostra_aprovada, q = quantile, acima = carteira_acima, abaixo = carteira_abaixo, verbose=verbose)

    if persist:
        carteira.to_csv(f"./data/carteiras/{nome_carteira}.csv")

    pad.verbose('line', level=2, verbose=verbose)
    return carteira




"""

    NOT CHANGED YET:

"""





    
def carteiraMomentum(prices, amostra_aprovada, quantile = 1/3, start= dt.date.today(), end= dt.date.today(), verbose=False):
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

def carteiraBeta(prices, amostra_aprovada, betas,quantile = 1/3, start= dt.date.today(), end= dt.date.today(), years = 3, verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "high_beta" ou "low_beta" de acordo com o beta
    '''
    pad.verbose("Montando carteiras de beta", level=3, verbose=verbose)

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
                betas.loc[d] = 0
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


def beta(Rm, Ra):
    return np.cov(Rm, Ra)[0][1]/st.variance(Rm)


"""

    CLASSIFICADORES

"""

def classificador_df(df, amostra_aprovada, q = 0.5, acima = 1, abaixo = -1, verbose=0):
    """
        Percorre um DataFrame classificando, linha a linha, os valores de cada coluna como acima ou abaixo da região interquantil

        Pré-condição:
            df.shape[0] == amostra_aprovada.shape[0]

        
        Retorna um DataFrame contendo as classificações
    """
    if df.shape[0] != amostra_aprovada.shape[0]:
        raise ValueError(f"df.shape != amostra_aprovada.shape: df.shape = {df.shape}; amostra_aprovada.shape = {amostra_aprovada.shape}")
    if df.shape[1] != amostra_aprovada.shape[1]:
        amostra_aprovada = amostra_aprovada[list(df.columns)]

    result = pd.DataFrame(index=df.index, columns=df.columns)

    for i in df.index:
        pad.verbose(f"Classificando carteiras para {i}", level=4, verbose=verbose)
        result.loc[i] = classificador_lista(list(df.loc[i]), list(amostra_aprovada.loc[i]), q, acima, abaixo)

    return result



def classificador_lista(lista, amostra_aprovada, q = 0.5, acima = 1, abaixo = -1):
    """
        Classifica os valores de uma lista em acima ou abaixo da região interquantil.
        Se o valor estiver dentro da região, retorna 0.

        q = 0.5 representa a mediana
        0 < q <= 0.5

        retorna uma lista de strings contendo as classificações
    """

    aux = [lista[i] for i in range(len(lista)) if (lista[i] != 0 and lista[i] != None and amostra_aprovada[i] )]

    if len(aux) == 0:
        result = [None for i in lista]   
    else:
        inf = np.quantile(aux, q)
        sup = np.quantile(aux, 1-q)

        result = [ classificador_valor(lista[i], inf, sup, acima, abaixo) if amostra_aprovada[i] else classificador_valor(None, inf, sup, acima, abaixo) for i in range(len(lista)) ]

    return result

def classificador_valor(valor, limite_inferior, limite_superior, acima = 1, abaixo = -1 ):
    result = 0
    if valor != None:
        if valor < limite_inferior:
            result = abaixo
        elif valor > limite_superior:
            result = acima

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






'''
    FUNÇÕES AUXILIARES
'''

def to_df(dic, indexes):
    result = pd.DataFrame(index= indexes)
    for key in dic:
        try:
            result[key] = dic[key]
        except:
            result[key] = util.eliminate_duplicates_indexes(dic[key])
    
    result.dropna(axis="index", how="all", inplace=True)

    return result



def get_first_day_of_year(array):
    result = list()
    years = set()
    for d in array:
        if d.year not in years:
            result.append( d )
            years.add(d.year)
    return result

def validate_returns_dates(asset, benchmark):
    result = pd.DataFrame(columns=["stock", "benchmark"])
    benchmark_dates = set(benchmark.index)
    for d in asset.index:
        if d in benchmark_dates:
            result.loc[d] = [ asset["returns"].loc[d], benchmark["returns"].loc[d] ]
    return result

