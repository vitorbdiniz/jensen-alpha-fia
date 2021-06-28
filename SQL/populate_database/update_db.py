import pandas as pd
import datetime as dt

from scripts.database.env import risk_factors_db
from scripts.database import matrixDB
from SQL.populate_database import connection

def update_time_dimension(database=risk_factors_db(), end=dt.date.today(), verbose=0 ):
    start = get_last_date(database, verbose=verbose) + dt.timedelta(days=1)
    date_range = pd.date_range(start, end, freq='D')
    values = ''

    for i in range(len(date_range)):
        date = date_range[i]
        values += f"('{str(date.date())}', {date.year}, {date.month}, {date.day})"        
        values += ';' if i == len(date_range)-1 else ','

    insert="INSERT INTO time_dimension(`date_`, `year`, `month`, `day`) VALUES " + values
    connection.execute_DML(database, insert, verbose=verbose)

    return True

def get_last_date(database, verbose=0):
    df = connection.execute_query(database, query='SELECT MAX(date_) FROM time_dimension;', verbose=verbose)
    last_date = df[0].iloc[0]
    return last_date