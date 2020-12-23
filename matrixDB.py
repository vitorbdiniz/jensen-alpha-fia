import pymysql
import sqlalchemy as sql

import pandas as pd
import numpy as np
from os.path import realpath


class SQLError(RuntimeError):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

'''
connecting to TC-Matrix's databank
'''
def connect_Matrix(environment = "prod"):
    if environment == "prod":
        host = "10.55.192.17"
        user = "vitor.diniz"
        password = "-uV3Fg*yA^xh?2VR&tAu6LH"
        dbname = "tc_matrix"
    elif environment == "hml":
        host = "10.249.240.10"
        user = "mmuser"
        password = "TradersPetr4"
        dbname = "tc_matrix"
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





    