import pandas as pd
import datetime as dt
from scipy.stats import zscore
from statistics import mean

import matrixDB
import util
import padding as pad

def carteiraQuality(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), verbose=0):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
    '''

    profitability = get_profitability(prices, amostra_aprovada, verbose)
    print(profitability)
    exit(1)
    # Growth = z (zΔgpoa + zΔroe + zΔroa + zΔcfoa + zΔgmar)
    # Safety = z(zbab + zlev + zo + zz + zevol)
    # Quality = z (Profitabiliy + Growth + Safety)



    #TODO
    return

def get_profitability(prices, amostra_aprovada, verbose=0):
    #z (z_gpoa + zroe + zroa + zcfoa + zgmar + zacc)
    result = pd.DataFrame()
    df = matrixDB.get_profitability_data(verbose=verbose)
    for ticker in prices.keys():
        data = df[df["ticker"]==ticker]
        result[ticker] = calculate_profitability(data)
    return result

def calculate_profitability(data, verbose = 0):
    df = process_data(data)
    df_zscores = z(df)

    result = []
    for index in df_zscores.index:
        result.append( mean(df_zscores.loc[index].tolist()) )
    return pd.Series(result, index=df_zscores.index)

def process_data(data=pd.DataFrame()):
    data.index = data["data_referencia"]
    data.drop(columns=["data_referencia", "ticker", "codigo_cvm", "demonstrativo_id", "nome_demonstrativo"], inplace=True)

    LTM(data, columns=["receita", "custos"])
    variation(data, columns=["wc"])

    GPOA = [] # (Receita - Custos)/ativo_médio 
    CFOA = [] # (Receita + D&A - ΔWC - CAPEX)/Ativo_médio
    ACC  = [] # (D&A - ΔWC) / ativo_médio
    GMAR = [] # (Receita - Custos)/receita
    for i in range(data.shape[0]):
        GPOA.append( (data["receita"].iloc[i]- data["custos"].iloc[i]) ) / data["ativos"].iloc[i]
        CFOA.append( (data["receita"].iloc[i] + data["depreciacao"].iloc[i] + data["wc"].iloc[i] - data["capex"].iloc[i]) ) / data["ativos"].iloc[i]
        ACC.append( data["depreciacao"].iloc[i] - data["wc"].iloc[i] )/ data["ativos"].iloc[i]
        GMAR.append( data["receita"].iloc[i] - data["custos"].iloc[i] ) / data["receita"].iloc[i]

    result = data[["ROE", "ROA"]]
    result["G"]
    result["GPOA"] = GPOA 
    result["CFOA"] = CFOA 
    result["GMAR"] = GMAR 
    result["ACC"]  = ACC
    return result

def variation(df, columns):
    for c in columns:
        aux = []
        for i in range(1, df.shape[0]):
            aux.append( df[c].iloc[i] - df[c].iloc[i-1] )
        df[c] = aux
    return 

def ITR(data, columns):
    for c in columns:
        aux = []
        for i in range(data.shape[0]):
            if type(data[c].iloc[i]) != type(1):
                data[c].iloc[i] = data[c].iloc[i].tolist()[0]
            if i >= 3 and util.get_month(data[c].iloc[i]) == 12:
                aux.append( data[c].iloc[i] - data[c].iloc[i-1] - data[c].iloc[i-2] - data[c].iloc[i-3])
            else:
                aux.append( data[c].iloc[i] )
        data[c] = aux
    return   

def LTM(data, columns, compute_itr = True):
    if compute_itr:
        ITR(data, columns)
    for c in columns:
        aux = []
        for i in range(data.shape[0]):
            if i >= 3:
                aux.append( data[c].iloc[i] + data[c].iloc[i-1] + data[c].iloc[i-2] + data[c].iloc[i-3] )
            else:
                aux.append( sum(data[c].iloc[0:i].tolist()) )
        data[c] = aux


def z(df):
    result = pd.DataFrame()
    for col in df.columns:
        aux = []
        for i in range(df.shape[0]):
            aux.append( zscore(df[col].iloc[0:i+1].tolist())[-1] )
        result[col] = aux

    return result
