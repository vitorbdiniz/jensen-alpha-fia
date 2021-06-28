import pandas as pd

#Comunicação com sistema
from scripts.data.busca_dados import get_prices
from scripts.data.criterios_elegibilidade import criterios_elegibilidade

from scripts.carteiras.formacao_carteiras import forma_carteiras
from scripts.fatores.fatores_risco import calcula_fatores_risco, nefin_factors
from scripts.database.matrixDB import get_tickers

from scripts.util import util, padding as pad

def busca_cotacoes(start, end, tickers = "all", verbose=0, test=False):
	pad.verbose("- INICIANDO PROCEDIMENTO DE BUSCA DE COTAÇÕES -", level=1, verbose=verbose)
	if test:
		tickers = list(pd.read_csv("./data/ticker_list.csv", index_col=0)["tickers"])
		prices = dict()
		for ticker in tickers:
			prices[ticker] = pd.read_csv("./data/prices/" + ticker + ".csv", index_col=0)
			prices[ticker].index = pd.DatetimeIndex([util.str_to_date(x) for x in prices[ticker].index])
	else:
		prices = get_prices(tickers, start, end, verbose=verbose)

	pad.verbose("line", level=1, verbose=verbose)
	return prices

def monta_amostras(prices, start, end, criterio_liquidez=0.8, verbose=0, test=False):
	pad.verbose("- INICIANDO PROCEDIMENTO DE AVALIAÇÃO DA AMOSTRA -", level=1, verbose=verbose)
	if test:
		amostra_aprovada = pd.read_csv("./data/criterios/amostra_aprovada.csv", index_col=0)
		amostra_aprovada.index = pd.DatetimeIndex([util.str_to_date(x) for x in amostra_aprovada.index])	

	else:
		amostra_aprovada = criterios_elegibilidade(prices, start = start, end = end, criterion = criterio_liquidez, verbose = verbose)

	pad.verbose("line", level=1, verbose=verbose)
	return amostra_aprovada

def monta_carteiras(prices, amostra_aprovada, quantile, start, end, verbose=0, test=False):
	pad.verbose("- INICIANDO PROCEDIMENTO DE FORMAÇÃO DE CARTEIRAS -", level=1, verbose=verbose)
	if test:
		carteiras = dict()
		carteiras["value"] = pd.read_csv("./data/carteiras/value.csv", index_col=0)
		carteiras["size"] = pd.read_csv("./data/carteiras/size.csv", index_col=0)
		carteiras["liquidity"] = pd.read_csv("./data/carteiras/liquidity.csv", index_col=0)
		carteiras["momentum"] = pd.read_csv("./data/carteiras/momentum.csv", index_col=0)
		carteiras["BAB"] = pd.read_csv("./data/carteiras/BAB.csv", index_col=0)
		#carteiras["quality"] = pd.read_csv("./data/carteiras/quality.csv", index_col=0)
		for c in carteiras:
			carteiras[c].index = pd.DatetimeIndex([util.str_to_date(x) for x in carteiras[c].index])
	else:
		carteiras = forma_carteiras(prices, amostra_aprovada, quantile, start=start, end=end, verbose=verbose)

	pad.verbose("line", level=1, verbose=verbose)
	return carteiras

def monta_fatores(prices, carteiras, start, end, verbose=0, longshort=False, test=False):
	pad.verbose("- INICIANDO PROCEDIMENTO DE CÁLCULO DE FATORES DE RISCO -", level=5, verbose=verbose)
	if test:
		fatores_risco = nefin_factors()
		fatores_risco.to_csv("./data/fatores/risk_factors.csv")
		#fatores_risco = pd.read_csv("./data/fatores/fatores_risco.csv", index_col=0)
	else:
		fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, longshort=longshort, verbose=verbose)
		
	pad.verbose("line", level=1, verbose=verbose)
	return fatores_risco

