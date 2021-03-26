#bibliotecas Python
import pandas as pd
import datetime as dt


#Comunicação com sistema
from scripts.data.busca_dados import get_prices
from scripts.data.criterios_elegibilidade import criterios_elegibilidade

from scripts.carteiras.formacao_carteiras import forma_carteiras
from scripts.fatores.fatores_risco import calcula_fatores_risco, nefin_factors
from scripts.database.matrixDB import get_tickers

from scripts.alpha.fundos_investimento import preprocess_fis
from scripts.alpha.decompose import decompose_all_by_factors
from scripts.alpha.alpha import jensens_alpha

from scripts.util import padding as pad
from scripts.util import util


def factors_complete_routine(start, end, source = "yahoo", quantile = 0.5,criterio_liquidez = 0.8,test = False,verbose = 0,persist = False):
	"""
		Calcula todos os fatores para o todo o período selecionado
		Rotina:
			1. Cálculo de preços
			2. Aprovação de amostras
			3. Montagem de carteiras
			4. Cálculo de fatores
	"""

	#### Busca de preços de ações
	prices = busca_cotacoes(True, start, end, verbose, source, persist)

	#### Avaliação da amostra
	amostra_aprovada = monta_amostras(prices, True, start, end, criterio_liquidez, verbose, persist)

	#### Formação de carteiras para cada período
	carteiras = monta_carteiras(prices, amostra_aprovada, quantile, test, start, end, verbose, persist)

	#### Cálculo de fatores de risco
	fatores_risco = monta_fatores(prices, carteiras, start, end, test, verbose, persist)

	pad.verbose("- FIM -", level=1, verbose=verbose)
	return fatores_risco


def busca_cotacoes(test, start, end, verbose, get_from, persist):
	pad.verbose("- INICIANDO PROCEDIMENTO DE BUSCA DE COTAÇÕES -", level=1, verbose=verbose)
	if test:
		tickers = list(pd.read_csv("./data/ticker_list.csv", index_col=0)["tickers"])
		prices = dict()
		for ticker in tickers:
			prices[ticker] = pd.read_csv("./data/prices/" + ticker + ".csv", index_col=0)
			prices[ticker].index = pd.DatetimeIndex([util.str_to_date(x) for x in prices[ticker].index])
	else:
		tickers = "all"
		prices = get_prices(tickers, start, end, verbose=verbose, get_from=get_from)
		pad.persist_collection(prices, path="./data/prices/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo preços. Não interrompa a execução. -")

	pad.verbose("line", level=1, verbose=verbose)
	return prices

def monta_amostras(prices, test, start, end, criterio_liquidez, verbose, persist):

	pad.verbose("- INICIANDO PROCEDIMENTO DE AVALIAÇÃO DA AMOSTRA -", level=1, verbose=verbose)
	if test:
		amostra_aprovada = pd.read_csv("./data/criterios/amostra_aprovada.csv", index_col=0)
		amostra_aprovada.index = pd.DatetimeIndex([util.str_to_date(x) for x in amostra_aprovada.index])	

	else:
		amostra_aprovada = criterios_elegibilidade(prices, start = start, end = end, criterion = criterio_liquidez, verbose = verbose)
		pad.persist(amostra_aprovada, path="./data/criterios/amostra_aprovada.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo amostra avaliada. Não interrompa a execução. -")
	
	pad.verbose("line", level=1, verbose=verbose)
	return amostra_aprovada

def monta_carteiras(prices, amostra_aprovada, quantile, test, start, end, verbose, persist):
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
		carteiras = forma_carteiras(prices, amostra_aprovada, quantile, start, end, verbose)
		pad.persist_collection(carteiras, path="./data/criterios/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo carteiras. Não interrompa a execução. -")

	pad.verbose("line", level=1, verbose=verbose)
	return carteiras

def monta_fatores(prices, carteiras, start, end, test, verbose, persist):
	pad.verbose("- INICIANDO PROCEDIMENTO DE CÁLCULO DE FATORES DE RISCO -", level=5, verbose=verbose)
	if test:
		fatores_risco = nefin_factors()
		fatores_risco.to_csv("./data/fatores/risk_factors.csv")
		#fatores_risco = pd.read_csv("./data/fatores/fatores_risco.csv", index_col=0)
	else:
		fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, verbose)
		pad.persist(fatores_risco, path="./data/criterios/fatores_risco.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo fatores de risco. Não interrompa a execução. -")
		
	pad.verbose("line", level=1, verbose=verbose)
	return fatores_risco

def monta_alphas(fatores_risco, fatores, test, persist, verbose): #TODO
	pad.verbose("- INICIANDO PROCEDIMENTO DE CÁLCULO DO ALFA DE JENSEN -", level=1, verbose=verbose)	

	fundos = pd.read_csv("./data/cotas_fias.csv")
	fis = preprocess_fis(fundos, verbose=verbose)
	if persist:
		for fund in fis:
			fis[fund].to_csv("./data/alphas/check/"+str(fund)+".csv")

	if test:
		alphas = dict()
		alphas['ALASKA BLACK INSTITUCIONAL FUNDO DE INVESTIMENTO DE ACOES'] = pd.read_csv("./data/alphas/ALASKA BLACK INSTITUCIONAL FUNDO DE INVESTIMENTO DE ACOES.csv", index_col=0)	
		alphas['COSMOS CAPITAL FUNDO DE INVESTIMENTO MULTIMERCADO - CRÉDITO PRIVADO INVESTIMENTO NO EXTERIOR'] = pd.read_csv("./data/alphas/COSMOS CAPITAL FUNDO DE INVESTIMENTO MULTIMERCADO - CRÉDITO PRIVADO INVESTIMENTO NO EXTERIOR.csv", index_col=0)
		alphas['DYNAMO COUGAR FUNDO DE INVESTIMENTO EM AÇÕES'] = pd.read_csv("./data/alphas/DYNAMO COUGAR FUNDO DE INVESTIMENTO EM AÇÕES.csv", index_col=0)
		alphas['REAL INVESTOR FUNDO DE INVESTIMENTO EM COTAS DE FUNDO DE INVESTIMENTO EM AÇÕES BDR NÍVEL I'] = pd.read_csv("./data/alphas/REAL INVESTOR FUNDO DE INVESTIMENTO EM COTAS DE FUNDO DE INVESTIMENTO EM AÇÕES BDR NÍVEL I.csv", index_col=0)
	else:
		alphas = jensens_alpha(fatores_risco, fis, fatores=fatores,verbose=verbose)
		pad.persist_collection(alphas, path="./data/alphas/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo alfas. Não interrompa a execução. -")

	return alphas



