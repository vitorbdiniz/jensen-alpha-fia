import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import util

def jensens_alpha(risk_factors, portfolios_returns, verbose=False):
    if verbose:
        print("Pré-processando dados de fundos de investimento")
    alphas = dict()
    fis = preprocess_fis(portfolios_returns)
    i=1
    for each_fund in fis:
        if verbose:
            print(str(i)+". Calculando alfa do Fundo " + fis[each_fund]["fundo"].iloc[0] + " ---- faltam "+str(len(fis)-i))
            i+=1
        data = preprocess_dates(fis[each_fund], risk_factors)
        expected = expected_returns(data)
        alpha = get_alpha(expected=expected, actual=data["cotas"])
        alphas[each_fund] = alpha
    return alphas

def get_alpha(expected, actual):
    alphas = []
    for i in range(len(expected)):
        alphas += [ actual[i] - expected[i] ]
    return alphas

def preprocess_fis(fundos):
    '''
        Recebe um DataFrame com retornos de fundos e retorna um dicionário de fundos
        chaves = codigos
        valores = DataFrames
    '''
    fis = dict()
    for i in range(fundos.shape[0]):
        df = fundos.iloc[i]
        if fundos["codigo"].iloc[i] not in fis:
            fis[fundos["codigo"].iloc[i]] = pd.DataFrame()
        fis[fundos["codigo"].iloc[i]] = fis[fundos["codigo"].iloc[i]].append(df, ignore_index=True)
    return fis


def preprocess_dates(fundo, fatores):
    '''
        Compara datas entre os dataframes de fundos e fatores, mantendo apenas datas existentes nos dois.
    '''
    fatores.dropna(inplace=True)
    fundo.dropna(inplace=True)
    nome,cotas,fator_mercado, fator_tamanho, fator_valor, fator_liquidez, fator_momentum ,dates = [],[],[],[],[],[],[],[]          
    for i in range(fundo.shape[0]):
        if fundo["data"].iloc[i] in fatores.index:
            cotas += [fundo["variacao"].iloc[i]]
            fator_mercado += [fatores.loc[fundo["data"].iloc[i]]
                              ["fator_mercado"]]
            fator_tamanho += [fatores.loc[fundo["data"].iloc[i]]
                              ["fator_tamanho"]]
            fator_valor += [fatores.loc[fundo["data"].iloc[i]]["fator_valor"]]
            fator_liquidez += [fatores.loc[fundo["data"].iloc[i]]
                               ["fator_liquidez"]]
            fator_momentum += [fatores.loc[fundo["data"].iloc[i]]
                               ["fator_momentum"]]
            dates += [fundo["data"].iloc[i]]
            nome += [fundo["fundo"].iloc[i]]

    result = pd.DataFrame({"dates":dates,"fundo":nome, "cotas": cotas, "fator_mercado": fator_mercado, "fator_tamanho": fator_tamanho, "fator_valor": fator_valor, "fator_liquidez" : fator_liquidez, "fator_momentum" : fator_momentum})
    return result.drop(labels=0, axis="index")

def expected_returns(data):
    """
        Calcula os retornos esperados para os fatores dados
    """
    X = data[["fator_mercado"	,"fator_tamanho"	,"fator_valor"	,"fator_liquidez"	,"fator_momentum"]]
    y = data[["cotas"]]
    pricing_model = LinearRegression().fit(X,y)

    R = pricing_model.predict(X)
    expected = []
    for list_ in R:
        for e in list_:
            expected += [e]
    return expected

