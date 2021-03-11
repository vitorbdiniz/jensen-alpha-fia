import datetime as dt
import pandas as pd
import numpy as np

from util import rearange_prices
import padding as pad

from carteira_tamanho import get_market_caps
from carteira_valor import get_all_book_to_market
from carteira_liquidez import get_liquidities
from carteira_momentum import get_momentum
from carteira_BAB import get_all_betas
from fator_qualidade import carteiraQuality 

"""

    FORMAÇÃO DE CARTEIRAS

"""

def forma_carteiras(prices, amostra_aprovada, quantile=1/3, start= dt.date.today(), end= dt.date.today(), verbose=0):
    carteiras = dict()

    #betas = getBeta(prices, amostra_aprovada,start, end, verbose)
    #betas.to_csv("./data/alphas/betas.csv")
    #betas = pd.read_csv("./data/alphas/betas.csv", index_col=0)

    closing_prices = rearange_prices(prices, start, end, column = "Adj Close")
    volumes = rearange_prices(prices, start, end, column = "Volume")

    carteiras['size']       = monta_carteiras("tamanho", "big", "small", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)
    carteiras['value']      = monta_carteiras("valor", "high", "low", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)
    carteiras['momentum']   = monta_carteiras("momentum", "winner", "loser", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)
    carteiras['liquidity']  = monta_carteiras("liquidez", "illiquid", "liquid", {"volumes":volumes, "prices":closing_prices}, amostra_aprovada, quantile, rejected=[30, None], start=start, end=end, verbose=verbose)
    carteiras['BAB']        = monta_carteiras("BAB", "high_beta", "low_beta", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)
    
    #carteiras['quality']    = monta_carteiras("qmj", "quality", "junk", closing_prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)
    
    return carteiras

"""

    FORMAÇÃO DE CADA CARTEIRA

"""
def monta_carteiras(nome_carteira, carteira_acima, carteira_abaixo, prices, amostra_aprovada, quantile, rejected = [0,None], start=dt.date(2010, 1, 1), end = dt.date.today(), verbose = 0):
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
        carteira = get_liquidities(quotations=prices, dates=amostra_aprovada.index, tickers=amostra_aprovada.columns, verbose=verbose)
    
    elif nome_carteira.lower() == "momento" or nome_carteira.lower() == "momentum" or nome_carteira.lower() == "mom" or nome_carteira.lower() == "wml":
        carteira = get_momentum(prices=prices, dates=amostra_aprovada.index, tickers=amostra_aprovada.columns, verbose=verbose)
    
    elif nome_carteira.lower() == "beta" or nome_carteira.lower() == "bab" or nome_carteira.lower() == "betting against beta":
        carteira = get_all_betas(prices=prices, start=start, end = end, method = "standard", verbose = verbose)
    
    elif nome_carteira.lower() == "quality" or nome_carteira.lower() == "qmj" or nome_carteira.lower() == "qualidade":
        carteira = 0 #TODO
    
    else:
        raise ValueError(f"nome_carteira mal especificado: nome_carteira = {nome_carteira}")
    
    carteira = classificador_df(carteira, amostra_aprovada, q = quantile, acima = carteira_acima, abaixo = carteira_abaixo, rejected=rejected, verbose=verbose)
    carteira.dropna(how="all", inplace=True)
    
    pad.verbose('line', level=2, verbose=verbose)
    return carteira


"""

    CLASSIFICADOR DE CARTEIRAS

"""

def classificador_df(df:pd.DataFrame, amostra_aprovada:pd.DataFrame, q = 0.5, acima = 1, abaixo = -1, rejected = [0,None], verbose=0):
    """
        Percorre um DataFrame classificando, linha a linha, os valores de cada coluna como acima ou abaixo da região interquantil
        
        Retorna um DataFrame contendo as classificações
    """
    if df.shape[1] < amostra_aprovada.shape[1]:
        amostra_aprovada = amostra_aprovada[list(df.columns)]
    result = pd.DataFrame(index=df.index, columns=df.columns)

    for i in df.index:
        pad.verbose(f"Classificando carteiras para {i}", level=4, verbose=verbose)
        try:
            data = amostra_aprovada.index.get_loc(i, method="pad")
        except:
            continue
        result.loc[i] = classificador_lista(list(df.loc[i]), list(amostra_aprovada.iloc[data]), q, acima, abaixo, rejected)

    return result



def classificador_lista(lista, amostra_aprovada, q = 0.5, acima = 1, abaixo = -1, rejected = [0,None]):
    """
        Classifica os valores de uma lista em acima ou abaixo da região interquantil.
        Se o valor estiver dentro da região, retorna 0.

        q = 0.5 representa a mediana
        0 < q <= 0.5

        retorna uma lista de strings contendo as classificações
    """

    aux = [lista[i] for i in range(len(lista)) if (lista[i] not in rejected and amostra_aprovada[i] )]

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



