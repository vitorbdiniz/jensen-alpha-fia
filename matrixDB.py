import pymysql
import sqlalchemy as sql

import pandas as pd
import numpy as np
import datetime as dt

from os.path import realpath
from env import define_matrix_env

import util
import padding as pad

class SQLError(RuntimeError):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

'''
connecting to TC-Matrix's databank
'''
def connect_Matrix(environment = "prod"):
    host, user, password, dbname = define_matrix_env(environment)
    database = pymysql.connect(host=host, user=user, password=password, db=dbname)
    return database.cursor()

'''
execute a specific MySQL query
'''
def execute_sql(query,environment = "prod", verbose=False):
    cursor = connect_Matrix(environment=environment)
    try:
        if verbose:
            print('Executando consulta ao banco de dados')
        cursor.execute(query=query)
        df = pd.DataFrame(cursor.fetchall())
    except:
        raise SQLError('execute_sql()', 'Falha de consulta')
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
    return equity



def get_quality_data(environment = "prod", verbose = False):
    query = open(realpath("./SQL/qmj_profitability.sql"), 'r').read()
    profit = execute_sql(query, environment=environment, verbose=verbose)
    profit = profit.rename(columns={0:"codigo_cvm",  1:"ticker", 2:"sector_id", 3:"data_referencia",  4:"demonstrativo_id", 5: "nome_demonstrativo",6:"ativos",  7:"receita",  8:"custos", 9:"ROE",  10:"ROA",  11:"depreciacao", 12:"wc", 13:"capex"})    
    profit["ticker"] = [x.replace("$", "") for x in profit["ticker"]]
    return profit


    