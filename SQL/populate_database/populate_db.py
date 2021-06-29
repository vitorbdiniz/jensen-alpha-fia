import pandas as pd
import datetime as dt

from scripts.database.env import risk_factors_db
from scripts.database import matrixDB
from SQL.populate_database import connection

from scripts.rotinas import routines

from scripts.util.padding import verbose as Verbose


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

def populate_prices_table(prices, database=risk_factors_db(), verbose=0):
    i=1
    for ticker in prices.keys():
        try:
            Verbose(f'{i}. Persistindo preços de {ticker} ---- restam {len(prices.keys())-i} ---- status:', level=5, verbose=verbose, end=' ')
            populate_stock_prices_table(prices[ticker], ticker, database, verbose=verbose)
            status = 'OK'
        except:
            status = 'Abortado'
        finally:
            i+=1
            Verbose(status, level=5, verbose=verbose)
    return True

def populate_stock_prices_table(prices, ticker, database=risk_factors_db(), verbose=0):
    values = ''
    for i in range(prices.shape[0]):
        values += f"('{prices.index[i]}','{ticker}',{prices['High'].iloc[i]}, {prices['Low'].iloc[i]}, {prices['Open'].iloc[i]}, {prices['Close'].iloc[i]} , {prices['Volume'].iloc[i]}, {prices['Adj Close'].iloc[i]} )"
        values += ';' if i == prices.shape[0]-1 else ','
    insert = "INSERT INTO prices(`date_`, `ticker`, `high`, `low`, `open`, `close`, `volume`, `adj_close`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True

def populate_market_factor_table(market_factor=None, database=risk_factors_db(), verbose=0):
    if market_factor is None:
        market_factor = routines.single_factor_routine('MKT', dt.date(1994, 1, 1), dt.date.today(), verbose=verbose).dropna()
    values = ''
    for i in range(market_factor.shape[0]):
        values += f"('{market_factor.index[i]}','MKT',{market_factor['long'].iloc[i]}, {market_factor['short'].iloc[i]}, {market_factor['factor'].iloc[i]} )"
        values += ';' if i == market_factor.shape[0]-1 else ','

    insert="INSERT INTO risk_factors(`date_`, `factor_symbol`, `long_portfolio_value`, `short_portfolio_value`, `risk_factor_value`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True
