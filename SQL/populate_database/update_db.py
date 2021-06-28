import pandas as pd
import datetime as dt

from scripts.database.env import risk_factors_db
from scripts.database import matrixDB
from SQL.populate_database import connection

from scripts.data.busca_dados import get_prices
from scripts.util.padding import verbose as Verbose


def update_time_dimension(database=risk_factors_db(), end=dt.date.today(), verbose=0 ):
    start = get_last_date(database, verbose=verbose)
    if start == dt.datetime.today():
        return False
    start += dt.timedelta(days=1)
    date_range = pd.date_range(start, end, freq='D')
    values = ''

    for i in range(len(date_range)):
        date = date_range[i]
        values += f"('{str(date.date())}', {date.year}, {date.month}, {date.day})"        
        values += ';' if i == len(date_range)-1 else ','

    insert="INSERT INTO time_dimension(`date_`, `year`, `month`, `day`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True



def update_prices_table(prices=None, database=risk_factors_db(), verbose=0):
    if prices is None:
        start=connection.execute_query('SELECT MAX(date_) FROM prices;')[0].iloc[0] + dt.timedelta(days=1)
        prices = get_prices(start=start)
    i=1
    for ticker in prices.keys():
        try:
            Verbose(f'{i}. Persistindo preços de {ticker} ---- restam {len(prices.keys())-i} ---- status:', level=5, verbose=verbose, end=' ')
            update_stock_prices_table(prices[ticker], ticker, database, verbose=verbose)
            status = 'OK' 
        except:
            status = 'Abortado'
        finally:
            i+=1
            Verbose(status, level=5, verbose=verbose)
    return True


def update_stock_prices_table(prices, ticker, database=risk_factors_db(), verbose=0):
    values = ''
    for i in range(prices.shape[0]):
        values += f"('{prices.index[i]}','{ticker}',{prices['High'].iloc[i]}, {prices['Low'].iloc[i]}, {prices['Open'].iloc[i]}, {prices['Close'].iloc[i]} , {prices['Volume'].iloc[i]}, {prices['Adj Close'].iloc[i]} )"
        values += ';' if i == prices.shape[0]-1 else ','
    insert = "INSERT INTO prices(`date_`, `ticker`, `high`, `low`, `open`, `close`, `volume`, `adj_close`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True



def update_ticker_dimension(database=risk_factors_db(), exchange='B3', verbose=0 ):
    
    tickers = get_non_registered_tickers(database, verbose=verbose)
    if len(tickers) == 0:
        return False

    values = ''
    for i in range(len(tickers)):
        ticker = tickers[i]
        values += f"('{ticker}', '{exchange}')"
        values += ';' if i == len(tickers)-1 else ','

    insert="INSERT INTO ticker_dimension(`ticker`, `exchange`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True










def get_non_registered_tickers(database, verbose=0):
    tickers = [ x.replace("$", "") for x in list(matrixDB.get_tickers(environment = "prod", verbose = verbose)[3])]

    df = connection.execute_query(database, query='SELECT ticker FROM ticker_dimension;', verbose=verbose)
    tickers_registered = set(df[0])
    non_registered_tickers = [ticker for ticker in tickers if ticker not in tickers_registered]
    return non_registered_tickers


def get_last_date(database, verbose=0):
    df = connection.execute_query(database, query='SELECT MAX(date_) FROM time_dimension;', verbose=verbose)
    last_date = df[0].iloc[0]
    return last_date