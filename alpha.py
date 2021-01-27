import numpy as np
import pandas as pd

import statsmodels.api as sm
from statsmodels.tools import add_constant
from scipy.stats import zscore

import fundos_investimento as FI
import util

def jensens_alpha(risk_factors, portfolios_returns, fatores=["fator_mercado","fator_tamanho","fator_valor","fator_liquidez","fator_momentum", "fator_beta", "fator_qualidade"], verbose=False):
    """
        Calcula o Alfa de Jensen para os fundos fornecidos, a partir dos fatores previamente calculados

        Retorna um pandas.DataFrame com colunas: "Nome", "alfa" e os betas solicitados
    """
    if verbose:
        print("Calculando alfas dos fundos de investimento")
    columns = get_columns(fatores)
    alphas = dict()
    if type(portfolios_returns) == type(pd.DataFrame()):
        portfolios_returns = FI.preprocess_fis(portfolios_returns)
    i=1
    for each_fund in portfolios_returns:
        df = pd.DataFrame(columns=columns)
        if verbose:
            print(str(i)+". Calculando alfa do Fundo " + str(portfolios_returns[each_fund]["fundo"].iloc[0]) + " ---- faltam "+str(len(portfolios_returns.keys())-i))
            i+=1

        data = preprocess_dates(portfolios_returns[each_fund], risk_factors)
        for j in range(10, data.shape[0]):
            if verbose:
                print(str(i)+"."+str(j)+". Calculando alfa do Fundo " + str(portfolios_returns[each_fund]["fundo"].iloc[0]) + " para o dia " + str(data.index[j]) + "---- faltam "+str(len(data.index)-j))

        df.loc[data.index[j]] = get_factor_exposition(data.iloc[0:j+1], fatores, each_fund)
        alphas[each_fund] = df
    return alphas

def get_factor_exposition(df, fatores, name):
    """
        Realiza a regressão com base nos retornos do portfólio e nos fatores de risco calculados

        retorna uma lista: alfa + betas + tvalores + pvalores + fvalor + pvalor do fvalor + R² ajustado
    """
    data = preprocess_data(df, fatores)
    X = add_constant(data[fatores])
    y = data[["cotas"]]

    regr = sm.OLS(y,X).fit(use_t=True)

    util.write_file(path="./data/alphas/regression_tables/tabela_"+str(name)+": "+str(data.index[-1]) + ".txt", data=regr.summary())

    return regr.params.tolist() + regr.tvalues.tolist() + regr.pvalues.tolist() + [regr.fvalue]+[regr.f_pvalue]+[regr.rsquared_adj]

'''
    FUNÇÕES AUXILIARES
'''



def preprocess_data(data, fatores):
    data = outlier_treatment(data, method="iqr", quantile=0.25, mult=1.5)
    return data

def outlier_treatment(df, method, quantile=0.25, mult=1.5):
    if method == "iqr":
        result = outlier_treatment_by_iqr(df, quantile=quantile, mult=mult)
    else:
        result = outlier_treatment_by_zscore(df, mult=mult)
    return result

def outlier_treatment_by_zscore(df, mult=1.5):
    outliers = set()
    for factors in df:
        z = zscore(df[factors])
        for i in range(len(z)):
            if abs(z[i]) > mult:
                outliers.add(i)
    result = df.drop(outliers, axis="index")
    return result

def outlier_treatment_by_iqr(data, quantile=0.25, mult=1.5):
    cols = data.columns.tolist()
    outliers = set()
    for fac in cols:
        q75 = np.quantile([ float(x) for x in data[fac]], 1-quantile)
        q25 = np.quantile([ float(x) for x in data[fac]], quantile)
        iqr = q75 - q25
        upper, lower = q75 + iqr*mult , q25 - iqr*mult
        for i in data.index:
            num = data[fac].loc[i].iloc[-1] if type(data[fac].loc[i]) == type(pd.Series([])) else data[fac].loc[i]
            if num > upper or num < lower:
                outliers.add(i)
    result = data.drop(outliers, axis="rows")
    return result

def get_columns(fatores):
    fatores = ["alpha"] + fatores
    betas = []
    tvalor = []
    pvalor = []
    for f in fatores:
        factor = str(f).split("_")
        if len(factor) > 1:
            betas.append( "beta_" + str(f).split("_")[1])
            factor = factor[1]
        else:
            betas.append("alpha")
            factor = factor[0]
        pvalor.append("pvalue_" + factor)
        tvalor.append("tvalue_" + factor)
    result = betas + tvalor + pvalor + ["fvalue", "f_pvalue", "R_squared_adj"]
    return result



def preprocess_dates(fundo, fatores):
    '''
        Compara datas entre os dataframes de fundos e fatores, mantendo apenas datas existentes nos dois.
    '''
    fatores.dropna(inplace=True)
    fundo.dropna(inplace=True)
    nome,cotas,fator_mercado, fator_tamanho, fator_valor, fator_liquidez, fator_momentum, fator_beta, fator_qualidade,dates = [],[],[],[],[],[],[],[], [],[]
    for i in range(fundo.shape[0]):
        if fundo["data"].iloc[i] in fatores.index:
            cotas += [fundo["variacao"].iloc[i]]
            fator_mercado    += [fatores.loc[fundo["data"].iloc[i]]["fator_mercado"]]
            fator_tamanho    += [fatores.loc[fundo["data"].iloc[i]]["fator_tamanho"]]
            fator_valor      += [fatores.loc[fundo["data"].iloc[i]]["fator_valor"]]
            fator_liquidez   += [fatores.loc[fundo["data"].iloc[i]]["fator_liquidez"]]
            fator_momentum   += [fatores.loc[fundo["data"].iloc[i]]["fator_momentum"]]
            fator_beta      += [fatores.loc[fundo["data"].iloc[i]]["fator_beta"]]
            #fator_qualidade += [fatores.loc[fundo["data"].iloc[i]]["fator_qualidade"]]


            dates += [fundo["data"].iloc[i]]
            nome += [fundo["fundo"].iloc[i]]

    result = pd.DataFrame({"cotas": cotas, "fator_mercado": fator_mercado, "fator_tamanho": fator_tamanho, "fator_valor": fator_valor, "fator_liquidez" : fator_liquidez, "fator_momentum" : fator_momentum, "fator_beta":fator_beta}, index=dates)
    return result.drop(labels=result.index[0], axis="index")
