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
        tickers = matrixDB.get_tickers(environment = "prod", verbose = verbose)

    i = 1
    prices = dict()
    for t in tickers:
        if verbose:
            print(str(i) + ". Buscando preços de " + t + " ---- faltam " + str(len(tickers)-i))
            i+=1
        try:
            prices[t] = web.get_data_yahoo(t+".SA", start, end)
        except:
            if verbose:
                print("------- 404 -> Not found")
    return prices



def getSelic(start = dt.date.today(), end = dt.date.today()):
    start = util.dateReformat(start)
    end = util.dateReformat(end)
    url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv&dataInicial="+ start +"&dataFinal="+end
    selicBCB = pd.read_csv(url, sep=";")
    selicBCB["valor"] = [ x/100 for x in util.reformatDecimalPoint(selicBCB["valor"], to=".")]
    selicBCB["data"] = util.datesReformat(selicBCB["data"], False)
    selic = pd.DataFrame({"valor":list(selicBCB["valor"])}, index = selicBCB["data"])
    return selic