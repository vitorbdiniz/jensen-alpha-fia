import pandas as pd

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

