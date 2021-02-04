import pandas as pd
import numpy as np
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
    quality_indexes = get_quality(prices, amostra_aprovada, verbose=verbose)



    #TODO
    return

def get_quality(prices, amostra_aprovada, verbose=0):
    quality = pd.DataFrame()

    #df = matrixDB.get_quality_data(verbose=verbose)
    df = pd.read_csv("./data/profit.csv", index_col=0)
    i=1
    for ticker in prices.keys():
        pad.verbose(str(i)+". Calculando indicador de qualidade de "+ str(ticker) + " ---- restam "+str(len(prices.keys())-i), level=4, verbose=verbose)
        i+=1

        indicadores_profitability = process_data( pd.DataFrame(df[df["ticker"]==ticker]) )
        profitability = get_profitability(indicadores_profitability, verbose=verbose)
        print(profitability)
        exit(1)
        #growth = get_growth(df,amostra_aprovada, verbose) #z (zΔgpoa + zΔroe + zΔroa + zΔcfoa + zΔgmar)
        #safety = get_safety(df,amostra_aprovada, verbose) #z(zbab + zlev + zo + zz + zevol)
        #quality[ticker] = calculate_quality(profitabiliy, growth, safety, verbose)

    return quality

def get_profitability(data, verbose = 0):
    df_zscores = z(data)

    result = []
    for index in df_zscores.index:
        result.append( mean(df_zscores.loc[index].tolist()) )
    return pd.Series(result, index=df_zscores.index)

def kill_duplicates(df, check_column="demonstrativo_id"):
    duplicates = set()
    checked = set()
    for i in df.index:
        if df[check_column].loc[i] not in checked:
            checked.add( df[check_column].loc[i] )
        else:
            duplicates.add(i)
    result = df.drop(labels=duplicates, axis="index")
    return result

def process_data(df=pd.DataFrame()):
    data = kill_duplicates(df)
    return data
    data = ITR(data, columns=["receita", "custos"])
    data = LTM(data, columns=["receita", "custos"])

    print(data)

    data = data.drop(columns=["data_referencia", "ticker", "codigo_cvm", "demonstrativo_id", "nome_demonstrativo"])

    
    data = variation(data, columns=["wc"])

    GPOA = [] # (Receita - Custos)/ativo_médio 
    CFOA = [] # (Receita + D&A - ΔWC - CAPEX)/Ativo_médio
    ACC  = [] # (D&A - ΔWC) / ativo_médio
    GMAR = [] # (Receita - Custos)/receita
    for i in range(data.shape[0]):
        GPOA.append( (data["receita"].iloc[i]- data["custos"].iloc[i]) / data["ativos"].iloc[i] )                                                   if data["ativos"].iloc[i]  != 0 else GPOA.append(0)
        CFOA.append( (data["receita"].iloc[i] + data["depreciacao"].iloc[i] + data["wc"].iloc[i] - data["capex"].iloc[i])  / data["ativos"].iloc[i]) if data["ativos"].iloc[i]  != 0 else CFOA.append(0)
        ACC.append(   (data["depreciacao"].iloc[i] - data["wc"].iloc[i] ) / data["ativos"].iloc[i])                                                     if data["ativos"].iloc[i]  != 0 else ACC.append(0)
        GMAR.append(  (data["receita"].iloc[i] - data["custos"].iloc[i] ) / data["receita"].iloc[i])                                                   if data["receita"].iloc[i] != 0 else GMAR.append(0)

    result = data[["ROE", "ROA"]]
    result["GPOA"] = GPOA 
    result["CFOA"] = CFOA 
    result["GMAR"] = GMAR 
    result["ACC"]  = ACC
    return result

def variation(df, columns):
    result = df.copy()
    for c in columns:
        aux = []
        for i in range(1, df.shape[0]):
            aux.append( df[c].iloc[i] - df[c].iloc[i-1] )
        result[c] = [0]+aux
    return result

def ITR(data, columns):
    result = data.copy()
    for c in columns:
        aux = []
        for i in range(data.shape[0]):
            if i >= 3 and util.get_month(data[c].index[i]) == 12:
                aux.append( data[c].iloc[i] - data[c].iloc[i-1] - data[c].iloc[i-2] - data[c].iloc[i-3])
            else:
                aux.append( data[c].iloc[i] )
        result[c] = aux
    return result

def LTM(data, columns, compute_itr = True):
    result = data.copy()
    if compute_itr:
        data = ITR(data, columns)
    for c in columns:
        aux = []
        for i in range(data.shape[0]):
            if i >= 3:
                aux.append( data[c].iloc[i] + data[c].iloc[i-1] + data[c].iloc[i-2] + data[c].iloc[i-3] )
            else:
                aux.append( sum(data[c].iloc[0:i].tolist()) )
        result[c] = aux
    return result

def z(df):
    result = pd.DataFrame()
    for col in df.columns:
        aux = []
        for i in range(df.shape[0]):
            aux.append( zscore(df[col].iloc[0:i+1].tolist())[-1] )

        result[col] = pd.Series(aux, index=df.index)

    return result
