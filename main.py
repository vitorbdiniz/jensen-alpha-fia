#bibliotecas Python
import pandas as pd
import datetime as dt

#Comunicação com sistema
from busca_dados import get_prices, rearange_prices
from criterios_elegibilidade import criterios_elegibilidade
from formacao_carteiras import forma_carteiras
from fatores_risco import calcula_fatores_risco, test_factors
from alpha import jensens_alpha
from matrixDB import get_tickers
from fundos_investimento import preprocess_fis
from decompose import decompose_all_by_factors
import padding as pad

import util


#MENSURANDO TEMPO
import time
start_time = time.time()

def now():
	return time.time() - start_time


def main():
	
	#Parâmetros escolhidos
	##Tempo
	start = dt.date(2010, 1, 1)
	end = dt.date.today()

	##Liquidez 
	criterio_liquidez = 0.8 #liquidez em 80% dos períodos

	##Fonte
	get_from="yahoo"

	#parâmetros adicionais
	quantile = 0.25 #quartile
	fatores=["fator_mercado","fator_tamanho","fator_valor","fator_liquidez","fator_momentum"]#,"fator_beta"]#, "fator_qualidade"]
	verbose = 5 # 0 a 5
	persist = True
	test = True


	pad.verbose("- INICIANDO PROCEDIMENTO DE BUSCA DE COTAÇÕES -", level=1, verbose=verbose)
	pad.verbose("- "+ str( int(now()/60) ) +" minutes-", level=2, verbose=verbose)


	#### Busca preços de ações
	if test:
		tickers = list(pd.read_csv("./data/ticker_list.csv", index_col=0)["tickers"])
		prices = dict()
		for ticker in tickers:
			prices[ticker] = pd.read_csv("./data/prices/" + ticker + ".csv", index_col=0)
			prices[ticker].index = pd.DatetimeIndex([util.str_to_date(x) for x in prices[ticker].index])
	else:
		tickers = "all"
		prices = get_prices(tickers, start, end, verbose=verbose, get_from=get_from)
		
		pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)

		if persist:
			pad.verbose("- Persistindo preços. Não interrompa a execução. -", level=2, verbose=verbose)

			pd.DataFrame({"tickers": list(prices.keys())}).to_csv("./data/ticker_list.csv")
			for ticker in prices.keys():
				prices[ticker].to_csv("./data/prices/" + ticker + ".csv")
			pad.verbose("-- OK.", level=2, verbose=verbose)

	
	pad.verbose("- INICIANDO PROCEDIMENTO DE AVALIAÇÃO DA AMOSTRA -", level=1, verbose=verbose)
	
	if test:
		amostra_aprovada = pd.read_csv("./data/criterios/amostra_aprovada.csv", index_col=0)
		amostra_aprovada.index = pd.DatetimeIndex([util.str_to_date(x) for x in amostra_aprovada.index])	

	else:
		amostra_aprovada = criterios_elegibilidade(prices, start = start, end = end, criterion = criterio_liquidez, verbose = verbose)
		pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)
		if persist:
			pad.verbose("-- Persistindo preços. Não interrompa a execução. --", level=2, verbose=verbose)
			amostra_aprovada.to_csv("./data/criterios/amostra_aprovada.csv")
			pad.verbose("-- OK", level=2, verbose=verbose)

	prices = rearange_prices(prices, start, end, column = "Adj Close")

	pad.verbose("- INICIANDO PROCEDIMENTO DE FORMAÇÃO DE CARTEIRAS -", level=1, verbose=verbose)

	#### Forma carteiras para cada período
	if False:
		carteiras = dict()
		carteiras["value"] = pd.read_csv("./data/carteiras/value.csv", index_col=0)
		carteiras["size"] = pd.read_csv("./data/carteiras/size.csv", index_col=0)
		carteiras["liquidity"] = pd.read_csv("./data/carteiras/liquidity.csv", index_col=0)
		carteiras["momentum"] = pd.read_csv("./data/carteiras/momentum.csv", index_col=0)
		#carteiras["beta"] = pd.read_csv("./data/carteiras/beta.csv", index_col=0)
		#carteiras["quality"] = pd.read_csv("./data/carteiras/quality.csv", index_col=0)
	else:
		carteiras = forma_carteiras(prices, amostra_aprovada, quantile, start, end, verbose)
		pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)
		if persist:
			pad.verbose("-- Persistindo carteiras --", level=2, verbose=verbose)
			for carteira in carteiras:
				carteiras[carteira].to_csv("./data/carteiras/"+ carteira +".csv")
			pad.verbose("-- OK", level=2, verbose=verbose)


	exit(carteiras)














	#### Calculando fatores de risco
	pad.verbose("- INICIANDO PROCEDIMENTO DE CÁLCULO DE FATORES DE RISCO -", level=5, verbose=verbose)

	if False:
		
		fatores_risco = test_factors()
		fatores_risco.to_csv("./data/fatores/risk_factors.csv")
		#fatores_risco = pd.read_csv("./data/fatores/fatores_risco.csv", index_col=0)
	else:
		fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, verbose)
		
		pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)

		if persist:
			pad.verbose("-- Persistindo fatores de risco. Não interrompa a execução. --", level=2, verbose=verbose)
			fatores_risco.to_csv("./data/fatores/fatores_risco.csv")
			pad.verbose("-- OK", level=2, verbose=verbose)

	pad.verbose("- INICIANDO PROCEDIMENTO DE CÁLCULO DO ALFA DE JENSEN -", level=1, verbose=verbose)
	
	

	fundos = pd.read_csv("./data/cotas_fias.csv")
	fis = preprocess_fis(fundos, freq, verbose=verbose)
	pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)
	if persist:
		for fund in fis:
			fis[fund].to_csv("./data/alphas/check/"+str(fund)+".csv")

	if test:
		alphas = dict()
		alphas['CONSTELLATION INSTITUCIONAL FUNDO DE INVESTIMENTO EM COTAS DE FUNDOS DE INVESTIMENTO DE AÇÕES'] = pd.read_csv("./data/alphas/CONSTELLATION INSTITUCIONAL FUNDO DE INVESTIMENTO EM COTAS DE FUNDOS DE INVESTIMENTO DE AÇÕES.csv", index_col=0)
		alphas['ALASKA BLACK INSTITUCIONAL FUNDO DE INVESTIMENTO DE ACOES'] = pd.read_csv("./data/alphas/ALASKA BLACK INSTITUCIONAL FUNDO DE INVESTIMENTO DE ACOES.csv", index_col=0)	
		alphas['COSMOS CAPITAL FUNDO DE INVESTIMENTO MULTIMERCADO - CRÉDITO PRIVADO INVESTIMENTO NO EXTERIOR'] = pd.read_csv("./data/alphas/COSMOS CAPITAL FUNDO DE INVESTIMENTO MULTIMERCADO - CRÉDITO PRIVADO INVESTIMENTO NO EXTERIOR.csv", index_col=0)
		alphas['DYNAMO COUGAR FUNDO DE INVESTIMENTO EM AÇÕES'] = pd.read_csv("./data/alphas/DYNAMO COUGAR FUNDO DE INVESTIMENTO EM AÇÕES.csv", index_col=0)
		alphas['REAL INVESTOR FUNDO DE INVESTIMENTO EM COTAS DE FUNDO DE INVESTIMENTO EM AÇÕES BDR NÍVEL I'] = pd.read_csv("./data/alphas/REAL INVESTOR FUNDO DE INVESTIMENTO EM COTAS DE FUNDO DE INVESTIMENTO EM AÇÕES BDR NÍVEL I.csv", index_col=0)
		alphas['VERDE AM AÇÕES MASTER FUNDO DE INVESTIMENTO EM AÇÕES'] = pd.read_csv("./data/alphas/VERDE AM AÇÕES MASTER FUNDO DE INVESTIMENTO EM AÇÕES.csv", index_col=0)
	else:
		alphas = jensens_alpha(fatores_risco, fis, fatores=fatores,verbose=verbose)
		pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)
		if persist:
			for fund in alphas:
				alphas[fund].to_csv("./data/alphas/"+str(fund)+".csv")

	#pad.verbose("- INICIANDO PROCEDIMENTO DE DECOMPOSIÇÃO DE RETORNOS -", level=1, verbose=verbose)
	#decomposed_returns = decompose_all_by_factors(alphas, fatores_risco, verbose=verbose)

	#if persist:
	#	for fund in decomposed_returns:
	#		decomposed_returns[fund].to_csv("./data/returns_decomposition/"+str(fund)+".csv")			


	pad.verbose("- FIM -", level=1, verbose=verbose)
	pad.verbose("- "+ str( now()/60 ) +" minutes-", level=2, verbose=verbose)
	return


if __name__ == "__main__":
    main()