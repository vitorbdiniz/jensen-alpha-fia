import datetime as dt
import pandas as pd

from statistics import mean
from scipy.stats.mstats import winsorize

from scripts.util import util
from scripts.util import padding as pad
from scripts.data import busca_dados

def calcula_fatores_risco(prices=None, carteiras=None, start= str(dt.date.today()), end= str(dt.date.today()), fatores_desejados='all', longshort=False,verbose=0):
    '''
        prices
        carteiras 
        start
        end
        fatores_desejados: {list} fatores possíveis ['MKT','SMB','HML','IML','WML','BAB']
        longshort {boolean} Caso True, retorna fator, carteira long e carteira short. Senão, apenas fator
        verbose
    '''
    pad.verbose("line", level=2, verbose=verbose)
    if fatores_desejados == 'all' or fatores_desejados is None:
        fatores_desejados = ['MKT','SMB','HML','IML','WML','BAB']
    elif type(fatores_desejados) == str:
        fatores_desejados = [fatores_desejados]

    fatores_dict = {
        'MKT' : {'name':'market'   , 'long_name':'Ibov'     , 'short_name':'Risk Free'},
        'SMB' : {'name':'size'     , 'long_name':'small'    , 'short_name':'big'},
        'HML' : {'name':'value'    , 'long_name':'high'     , 'short_name':'low'},
        'IML' : {'name':'liquidity', 'long_name':'illiquid' , 'short_name':'liquid'},
        'WML' : {'name':'momentum' , 'long_name':'winner'   , 'short_name':'loser'},
        'BAB' : {'name':'BAB'      , 'long_name':'low_beta' , 'short_name':'high_beta'}
    }
    
    dates = pd.date_range(start=start, end=end)
    fatores = pd.DataFrame( index=dates )

    if longshort:
            long = pd.DataFrame( index=dates )
            short = pd.DataFrame( index=dates )
    if prices is not None:
        closing_prices = util.rearange_prices(prices, start, end, column = "Close")
        returns = pd.DataFrame({ticker : util.getReturns(closing_prices[ticker], form="Series") for ticker in closing_prices.columns}, index = closing_prices.index).dropna(how="all")
    
    for fac in fatores_desejados:
        if fac == 'MKT':
            factor_value = marketFactor(Rm="^BVSP", Rf = "selic", start=start, end=end, longshort=longshort, verbose=verbose)
        else:
            factor_value = calculate_factor_all_dates(carteiras[ fatores_dict[fac]['name'] ], returns, factor_name=fatores_dict[fac]['name'], nome_carteira_long=fatores_dict[fac]['long_name'], nome_carteira_short=fatores_dict[fac]['short_name'],  longshort=longshort, verbose=verbose)

        if longshort:
            factor_value, long_port, short_port = factor_value
            long[fac], short[fac] = long_port, short_port
        fatores[fac] = factor_value

    #fatores["MKT"], long["MKT"], short["MKT"]
    #fatores["SMB"], long["SMB"], short["SMB"] = calculate_factor_all_dates(carteiras["size"], returns, factor_name="tamanho", nome_carteira_long="small", nome_carteira_short="big",  verbose=verbose)
    #fatores["HML"], long["HML"], short["HML"] = calculate_factor_all_dates(carteiras["value"], returns, factor_name="valor", nome_carteira_long="high", nome_carteira_short="low",  verbose=verbose)
    #fatores["IML"], long["IML"], short["IML"] = calculate_factor_all_dates(carteiras["liquidity"], returns, factor_name="liquidez", nome_carteira_long="illiquid", nome_carteira_short="liquid",  verbose=verbose)
    #fatores["WML"], long["WML"], short["WML"] = calculate_factor_all_dates(carteiras["momentum"], returns, factor_name="momentum", nome_carteira_long="winner", nome_carteira_short="loser",  verbose=verbose)
    #fatores["BAB"], long["BAB"], short["BAB"] = calculate_factor_all_dates(carteiras["BAB"], returns, factor_name="beta", nome_carteira_long="low_beta", nome_carteira_short="high_beta",  verbose=verbose)
    #fatores["QMJ"] = calculate_factor_all_dates(carteiras["quality"], returns, factor_name="qualidade", nome_carteira_long="quality", nome_carteira_short="junk",  verbose=verbose)
    
    fatores.dropna(how="all", inplace=True)
    if longshort:
        long.dropna(how="all", inplace=True)
        short.dropna(how="all", inplace=True)
        fatores = {"fatores_risco":fatores, "long_scores":long, "short_scores":short}

    return fatores

def marketFactor(Rm = "^BVSP", Rf = "selic",start = str(dt.date.today()), end=str(dt.date.today()), longshort=False, verbose=0):   
    pad.verbose("- Calculando fator de risco de mercado -", level=2, verbose=verbose)
    
    ibov = busca_dados.get_prices(Rm, start, end, verbose=0)["^BVSP"]

    Rm = util.getReturns(ibov["Close"], form="Series")
    Rf = util.getSelic(start, end, form="Series")

    factor = Rm - Rf
    result = (factor, Rm, Rf) if longshort else factor

    pad.verbose("line", level=2, verbose=verbose)
    return result


def calculate_factor_all_dates(carteiras, returns, factor_name, nome_carteira_long, nome_carteira_short,  longshort=False, verbose=0):
    """

        Calcula fatores de risco para aqueles que possuem portfólios.

        Retorna pandas.Series com o cálculo diário do fator.

    """
    long = pd.Series({})
    short = pd.Series({})

    i=1
    for d in returns.index:
        pad.verbose(f"{i}. Calculando fator de risco de {factor_name} para o período {d}", level=5, verbose=verbose)
        i+=1
        if d >= carteiras.index[0]:
            portfolios = carteiras.iloc[carteiras.index.get_loc(d, method="pad")]
            long_mean, short_mean = calculate_factor(returns.loc[d], portfolios, nome_carteira_long, nome_carteira_short)

            long = long.append( pd.Series([long_mean], index=[d]) )
            short = short.append( pd.Series([short_mean], index=[d]) )

        else:
            pad.verbose(f"---- Carteira não encontrada para o período {d}", level=5, verbose=verbose)
            
    factor = long - short
    result = (factor, long, short) if longshort else factor

    pad.verbose("line", level=2, verbose=verbose)
    return result

def calculate_factor(returns, portfolios, long, short):
    returns = pd.Series( winsorize(returns.values, limits=[0.05,0.05], nan_policy='omit'), index = returns.index)
    portfolioLong = []
    portfolioShort = []
    for i in portfolios.index:
        if portfolios.loc[i] == long:
            portfolioLong.append(returns.loc[i])
        elif portfolios.loc[i] == short:
            portfolioShort.append(returns.loc[i])
    

    portfolioLong = util.none_to_zero(portfolioLong)
    portfolioShort = util.none_to_zero(portfolioShort)
    
    short_mean = None
    long_mean = None
    if len(portfolioLong) > 0:
        long_mean = mean(portfolioLong)
    if len(portfolioShort) > 0:
        short_mean = mean(portfolioShort)

    return (long_mean, short_mean)


def nefin_factors():
    concat_date = lambda date : [str(dt.date(date[0].iloc[i], date[1].iloc[i], date[2].iloc[i])) for i in range(len(date[0]))]#convert a list of years, months and dates into a list of dates

    mkt = pd.read_excel("http://nefin.com.br/Risk%20Factors/Market_Factor.xls") 
    hml = pd.read_excel("http://nefin.com.br/Risk%20Factors/HML_Factor.xls")    
    smb = pd.read_excel("http://nefin.com.br/Risk%20Factors/SMB_Factor.xls")    
    wml = pd.read_excel("http://nefin.com.br/Risk%20Factors/WML_Factor.xls")    
    iml = pd.read_excel("http://nefin.com.br/Risk%20Factors/IML_Factor.xls")    

    risk_factors = pd.DataFrame({"year":mkt["year"], "month":mkt["month"], "day":mkt["day"], "fator_mercado" : mkt["Rm_minus_Rf"], "fator_valor" : hml["HML"], "fator_tamanho" : smb["SMB"],"fator_momentum" : wml["WML"],"fator_liquidez" : iml["IML"]})
    risk_factors.index = concat_date([risk_factors["year"], risk_factors["month"], risk_factors['day']])
    risk_factors = risk_factors.drop(columns=["year", "month", "day"])

    return risk_factors


