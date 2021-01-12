import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression

import fundos_investimento as FI
import util

def jensens_alpha(risk_factors, portfolios_returns, fatores=["fator_mercado","fator_tamanho","fator_valor","fator_liquidez","fator_momentum", "fator_beta", "fator_qualidade"], verbose=False):
    """
        Calcula o Alfa de Jensen para os fundos fornecidos, a partir dos fatores previamente calculados

        Retorna um pandas.DataFrame com colunas: "Nome", "alfa" e os betas solicitados
    """
    if verbose:
        print("Calculando alfas dos fundos de investimento")
    columns = ["codigo","nome"] + betas_to_be_calculated(fatores) + ["alfa", "tvalor", "pvalor"]
    alphas = pd.DataFrame(columns = columns)
    if type(portfolios_returns) == type(pd.DataFrame()):
        portfolios_returns = FI.preprocess_fis(portfolios_returns)
    i=1
    for each_fund in portfolios_returns:
        if verbose:
            print(str(i)+". Calculando alfa do Fundo " + portfolios_returns[each_fund]["fundo"].iloc[0] + " ---- faltam "+str(len(portfolios_returns.keys())-i))
        data = preprocess_dates(portfolios_returns[each_fund], risk_factors)
        row = [portfolios_returns[each_fund]["codigo"].iloc[i], portfolios_returns[each_fund]["fundo"].iloc[i]] + get_factor_exposition(data, fatores)
        alphas.loc[i] = row 
        i+=1

    return alphas

def get_factor_exposition(data, fatores):
    """
        Realiza a regressão com base nos retornos do portfólio e nos fatores de risco calculados

        retorna uma lista: nome_fundo, alfa_fundo, betas_fundo
    """
    X = data[fatores]
    y = data[["cotas"]]
    regression = LinearRegression().fit(X, y)
    betas = list(regression.coef_[0])
    alpha = list([regression.intercept_[0]])
    expected = np.array([ x[0] for x in regression.predict(X)], dtype=float)
    y = np.array(y["cotas"].tolist(), dtype=float)
    t_stats = list(ttest_ind(y, expected, axis=None))
    return betas + alpha + t_stats


def betas_to_be_calculated(fatores):
    betas = []
    for f in fatores:
        betas.append( "beta_" + str(f).split("_")[1])
    return betas



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
            fator_mercado += [fatores.loc[fundo["data"].iloc[i]]["fator_mercado"]]
            fator_tamanho += [fatores.loc[fundo["data"].iloc[i]]["fator_tamanho"]]
            fator_valor += [fatores.loc[fundo["data"].iloc[i]]["fator_valor"]]
            fator_liquidez += [fatores.loc[fundo["data"].iloc[i]]["fator_liquidez"]]
            fator_momentum += [fatores.loc[fundo["data"].iloc[i]]["fator_momentum"]]
            #fator_beta += [fatores.loc[fundo["data"].iloc[i]]["fator_beta"]]
            #fator_qualidade += [fatores.loc[fundo["data"].iloc[i]]["fator_qualidade"]]


            dates += [fundo["data"].iloc[i]]
            nome += [fundo["fundo"].iloc[i]]

    result = pd.DataFrame({"dates":dates,"fundo":nome, "cotas": cotas, "fator_mercado": fator_mercado, "fator_tamanho": fator_tamanho, "fator_valor": fator_valor, "fator_liquidez" : fator_liquidez, "fator_momentum" : fator_momentum})
    return result.drop(labels=0, axis="index")

