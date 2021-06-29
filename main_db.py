import datetime as dt
from scripts.fatores.fatores_risco import marketFactor

from scripts.util.padding import verbose
from SQL.populate_database import populate_db, update_db

from scripts.data.busca_dados import get_prices


def populate(table, verbose=0):
    if table == 'time_dimension':
        populate_db.populate_time_dimension(start='1900-01-01', verbose=verbose)
    elif table == 'ticker_dimension':
        populate_db.populate_ticker_dimension(exchange='B3', verbose=verbose)
    elif table == 'market_factor':
        populate_db.populate_market_factor_table(verbose=verbose)
    elif table=='prices':
        prices = get_prices(start='2000-01-01', verbose=verbose)
        populate_db.populate_prices_table(prices, verbose=verbose)

def update(table, verbose=0):
    if table == 'time_dimension':
        update_db.update_time_dimension(verbose=verbose)
    elif table == 'ticker_dimension':
        update_db.update_ticker_dimension(exchange='B3', verbose=verbose)
    elif table == 'market_factor':
        update_db.update_market_factor_table(verbose=verbose)
    elif table=='prices':
        update_db.update_prices_table(verbose=verbose)


if __name__ == "__main__":
    verbose = 5
    for table in ['time_dimension', 'ticker_dimension', 'marketFactor', 'prices']:
        if table == 'ticker_dimension' or dt.date.today().isoweekday() in range(1, 6):
            update('market_factor', verbose=verbose)
