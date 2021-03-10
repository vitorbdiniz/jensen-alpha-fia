import busca_dados
import datetime as dt
import pandas as pd
from statistics import mean

from util import getSelic
import util
import padding as pad

def calcula_fatores_risco(prices, carteiras, start= str(dt.date.today()), end= str(dt.date.today()), verbose=False):
    
    pad.verbose("line", level=2, verbose=verbose)
    
    closing_prices = util.rearange_prices(prices, start, end, column = "Adj Close")
    returns = pd.DataFrame({ticker : util.getReturns(closing_prices[ticker], form="Series") for ticker in closing_prices.columns}, index = closing_prices.index).dropna(how="all")

    fatores = pd.DataFrame(index=returns.index)
    
    fatores["fator_mercado"]  = marketFactor(Rm="^BVSP", Rf = "selic", start=start, end=end, verbose=verbose)
    fatores["fator_tamanho"]  = calculate_factor_all_dates(carteiras["size"], returns, factor_name="tamanho", nome_carteira_long="small", nome_carteira_short="big",  verbose=verbose)
    fatores["fator_valor"]    = calculate_factor_all_dates(carteiras["value"], returns, factor_name="valor", nome_carteira_long="high", nome_carteira_short="low",  verbose=verbose)
    fatores["fator_liquidez"] = calculate_factor_all_dates(carteiras["liquidity"], returns, factor_name="liquidez", nome_carteira_long="illiquid", nome_carteira_short="liquid",  verbose=verbose)
    fatores["fator_momentum"] = calculate_factor_all_dates(carteiras["momentum"], returns, factor_name="momentum", nome_carteira_long="winner", nome_carteira_short="loser",  verbose=verbose)
    
    #fatores["fator_beta"]     = calculate_factor_all_dates(carteiras["beta"], returns, factor_name="beta", nome_carteira_long="low_beta", nome_carteira_short="high_beta",  verbose=verbose)
    #fatores["QMJ"] = calculate_factor_all_dates(carteiras["quality"], returns, factor_name="qualidade", nome_carteira_long="quality", nome_carteira_short="junk",  verbose=verbose)
    fatores.dropna(inplace=True)
    return fatores

def marketFactor(Rm = "^BVSP", Rf = "selic",start = str(dt.date.today()), end=str(dt.date.today()), verbose=0):   
    pad.verbose("- Calculando fator de risco de mercado -", level=2, verbose=verbose)
    result = pd.Series()
    
    ibov = busca_dados.get_prices(Rm, start, end, verbose=0)["^BVSP"]
    
    Rm = util.getReturns(ibov["Adj Close"], form="Series")
    Rf = getSelic(start, end, form="Series")
    indexes_set = set(Rf.index)
    
    i = 1
    for date in Rm.index:
        pad.verbose(f"{i}. Calculando fator mercado para o periodo {date} ---- restam {len(Rm.index)-i}", level=5, verbose=verbose)
        i += 1
        if date in indexes_set:
            result = result.append( pd.Series({ date : Rm.loc[date]- Rf.loc[date] }) )
    
    pad.verbose("line", level=2, verbose=verbose)

    return result


def calculate_factor_all_dates(carteiras, returns, factor_name, nome_carteira_long, nome_carteira_short,  verbose=0):
    """

        Calcula fatores de risco para aqueles que possuem portfólios.

        Retorna pandas.Series com o cálculo diário do fator.

    """
    pad.verbose(f"- Calculando fator de risco de {factor_name} -", level=2, verbose=verbose)
    factor = pd.Series({})

    for d in carteiras.index:
        year_returns = util.get_data_in_year(returns, year = d.year)
        partial = calculate_periodic_factors(carteiras.loc[d], year_returns, factor_name, nome_carteira_long, nome_carteira_short, verbose=verbose)
        factor = factor.append(partial)
    return factor


def calculate_periodic_factors(carteiras, returns, factor_name, nome_carteira_long, nome_carteira_short, verbose=0):

    portfolioLong = returns[ [ ticker for ticker in carteiras.index if carteiras.loc[ticker] == nome_carteira_long] ]
    portfolioShort = returns[ [ ticker for ticker in carteiras.index if carteiras.loc[ticker] == nome_carteira_short] ]

    factor = pd.Series({})

    i = 1
    for d in portfolioLong.index:
        pad.verbose(f"{i}. Calculando fator {factor_name} para o periodo {d} ---- restam {len(returns.index)-i}", level=5, verbose=verbose)
        i+=1
        factor = factor.append( pd.Series({ d : (mean(portfolioLong.loc[d]) - mean(portfolioShort.loc[d])) }) )
    return factor




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


