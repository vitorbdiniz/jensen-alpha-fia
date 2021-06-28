import pymysql
import pandas as pd

import numpy as np
import datetime as dt

from os.path import realpath
from scripts.database.env import env


'''
connecting to TC-Matrix's databank
'''
def connect_Matrix(environment = "prod"):
    credentials = env(environement=environment) 
    database = pymysql.connect(host=credentials.get_host(), user=credentials.get_user(), password=credentials.get_password(), db=credentials.get_dbname())
    return database.cursor()

'''
execute a specific MySQL query
'''
def execute_sql(query, environment = "prod", verbose=False):
    cursor = connect_Matrix(environment=environment)
    if verbose:
        print('Executando consulta ao banco de dados')
    cursor.execute(query=query)
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    return df

'''

funções de abstração da conexão com o BD 

'''

def get_tickers(environment = "prod", verbose = False):
    query = open(realpath("./SQL/getTickers.sql"), 'r').read()
    return execute_sql(query, environment=environment, verbose=verbose)

def get_stocks_quantity(environment = "prod", verbose = False):
    query = open(realpath("./SQL/stocks.sql"), 'r').read()
    stocks = execute_sql(query, environment=environment, verbose=verbose)

    stocks[0] = [x.replace("$", "") for x in stocks[0]]
    stocks.rename(columns={0:"codigo_negociacao", 1:"data_referencia", 2:"release_date", 3:"ordinarias", 4:"preferenciais", 5:"totais"}, inplace=True)
    return stocks


def get_account(account, environment = "prod", verbose = False):
    query = open(realpath("./SQL/stocks.sql"), 'r').read()
    query = query.replace(":code:", account)
    return execute_sql(query, environment=environment, verbose=verbose)

def get_equity(environment = "prod", verbose = False):
    query = open(realpath("./SQL/getEquity.sql"), 'r').read()
    equity = execute_sql(query, environment=environment, verbose=verbose)
    equity[0] = [x.replace("$", "") for x in equity[0]]
    equity.rename(columns={0:"codigo_negociacao",1:"codigo_cvm", 2:"demonstrativo_id", 3:"codigo_conta",4:"data_periodo",5:"release_date", 6:"ordinaria", 7:"preferencial", 8:"total", 9:"valor_conta", 10:"VPA"}, inplace=True)
    
    return equity



def get_quality_data(environment = "prod", verbose = False):
    query = open(realpath("./SQL/qmj_profitability.sql"), 'r').read()
    profit = execute_sql(query, environment=environment, verbose=verbose)
    profit = profit.rename(columns={0:"codigo_cvm",  1:"ticker", 2:"sector_id", 3:"data_referencia",  4:"demonstrativo_id", 5: "nome_demonstrativo",6:"ativos",  7:"receita",  8:"custos", 9:"ROE",  10:"ROA",  11:"depreciacao", 12:"wc", 13:"capex"})    
    profit["ticker"] = [x.replace("$", "") for x in profit["ticker"]]
    return profit


    