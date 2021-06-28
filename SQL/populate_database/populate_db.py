import pandas as pd
import datetime as dt

from scripts.database.env import risk_factors_db
from scripts.database import matrixDB
from SQL.populate_database import connection


def populate_time_dimension(database=risk_factors_db(), start=dt.date.today(), end=dt.date.today(), verbose=0 ):
    date_range = pd.date_range(start, end, freq='D')
    values = ''

    for i in range(len(date_range)):
        date = date_range[i]
        values += f"('{str(date.date())}', {date.year}, {date.month}, {date.day})"        
        values += ';' if i == len(date_range)-1 else ','

    insert="INSERT INTO time_dimension(`date_`, `year`, `month`, `day`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True

def populate_ticker_dimension(database=risk_factors_db(), exchange='B3', verbose=0 ):
    tickers = [ x.replace("$", "") for x in list(matrixDB.get_tickers(environment = "prod", verbose = verbose)[3])]
    values = ''

    for i in range(len(tickers)):
        ticker = tickers[i]
        values += f"('{ticker}', '{exchange}')"
        values += ';' if i == len(tickers)-1 else ','

    insert="INSERT INTO ticker_dimension(`ticker`, `exchange`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True
