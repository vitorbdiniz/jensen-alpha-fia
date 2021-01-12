import pandas as pd
import numpy as np

def preprocess_fis(fundos=pd.DataFrame(), verbose = False):
    '''
        Recebe um DataFrame com retornos de fundos e retorna um dicionário de fundos
        chaves = codigos
        valores = DataFrames
    '''
    if verbose:
        print("Pré-processando dados de fundos de investimento")
        codigo = fundos["codigo"].loc[0]
        j = 2
        print("1. Pré-processando dados de "+fundos["fundo"].loc[0])

    fis = dict()

    for i in fundos.index:
        if verbose:
            if fundos["codigo"].loc[i] != codigo:
                codigo = fundos["codigo"].loc[i]
                print(str(j) + ". Pré-processando dados de " +fundos["fundo"].loc[i])
                j += 1
        row = fundos.loc[i]
        if fundos["codigo"].loc[i] not in fis:
            fis[fundos["codigo"].loc[i]] = pd.DataFrame(columns=fundos.columns)
        fis[fundos["codigo"].loc[i]].loc[i] = row
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return fis

