import pandas as pd
import datetime as dt

from scripts.database.env import risk_factors_db
from SQL.populate_database import connection

from scripts.util.padding import verbose as Verbose



def get_prices(tickers = tuple(), start=dt.date(2010,1,1), end=dt.date.today(), database=risk_factors_db(), verbose=0):
    query = open('./SQL/get_prices.sql', 'r').read()
    
    query = query.replace(":start_date:", f" '{str(start)}' ")
    query = query.replace(":end_date:", f" '{str(end)}' ")
    if len(tickers) == 0 or tickers == 'all':
        query = query.replace('AND ticker IN :ticker_tuple:', '')
    else:
        tickers = tuple(tickers)
        query = query.replace(':ticker_tuple:', str(tickers))
    result = connection.execute_query(database, query, verbose=verbose)
    result.rename(columns={0: 'id',1: 'time_id',2:'date',3: 'ticker_id',4: 'ticker',5: 'High',6: 'Low',7: 'Open',8: 'Close',9: 'Volume',10: 'Adj Close'}, inplace=True)

    return result

