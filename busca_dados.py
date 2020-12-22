#Python libs
import datetime as dt
import pandas as pd
import pandas_datareader as web

#Workspace libs
import matrixDB
import util



def get_prices(tickers, start=dt.date.today(), end=dt.date.today(), verbose = False):
    '''
        Busca cotações de uma lista de ativos para um determinado intervalo de tempo

        Se tickers == lista de ações, então get_prices retorna as cotações dessa lista,
        senão, se tickers == "all", então o BD é acessado e todas as cotações são buscadas
    '''
    if tickers == "all":
        tickers = [ x.replace("$", "") for x in list(matrixDB.get_tickers(environment = "prod", verbose = verbose)[3])]
    elif str(tickers).lower() == "ibov" or str(tickers) == "^BVSP":
        tickers = ["^BVSP"]
    elif type(tickers) != type([]):
        raise AttributeError("ticker deve ser 'all' ou list")
    i = 1
    prices = dict()
    for t in tickers:
        if verbose:
            print(str(i) + ". Buscando preços de " + str(t) + " ---- faltam " + str(len(tickers)-i))
            i+=1
        try:
            if t[0] != '^':
                prices[t] = web.get_data_yahoo(t+".SA", start, end)
            else:
                prices[t] = web.get_data_yahoo(t, start, end)
        except:
            if verbose:
                print("------- 404 -> Not found")
    
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return prices



def getSelic(start = dt.date.today(), end = dt.date.today(), verbose = False):
    if verbose:
        print("Buscando série histórica da Selic")
    start = util.dateReformat(start)
    end = util.dateReformat(end)
    url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ start +"&dataFinal="+end
    selicBCB = pd.read_csv(url, sep=";")
    selicBCB["valor"] = [ x/100 for x in util.reformatDecimalPoint(selicBCB["valor"], to=".")]
    selicBCB["data"] = util.datesReformat(selicBCB["data"], False)
    selic = pd.DataFrame({"valor":list(selicBCB["valor"])}, index = selicBCB["data"])
    if verbose:
        print("-------------------------------------------------------------------------------------------")
    return selic


