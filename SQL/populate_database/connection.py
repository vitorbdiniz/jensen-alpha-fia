import pymysql
import pandas as pd
from scripts.util.padding import verbose as Verbose

'''
connecting to database
'''
def connect_database(database):
    database = pymysql.connect(host=database.get_host(), user=database.get_user(), password=database.get_password(), db=database.get_dbname())
    return database

'''
execute a specific MySQL query
'''
def mysql_cursor(database_credentials, code, def_type='DQL', verbose=0):
    database = connect_database(database_credentials)
    cursor = database.cursor()

    Verbose(f'Executando script {def_type}', level=3, verbose=verbose)
    
    cursor.execute(query=code)
    if def_type != 'DQL':
        Verbose(f'Realizando commit em {str(database_credentials)}', level=3, verbose=verbose)
        database.commit()
    return cursor

def execute_DML(database, code, verbose=0):
    cursor = mysql_cursor(database, code=code, def_type='DML', verbose=verbose)
    cursor.close()
    return None

def execute_query(database, query, verbose=0):
    cursor = mysql_cursor(database, code=query, def_type='DQL', verbose=verbose)
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    return df