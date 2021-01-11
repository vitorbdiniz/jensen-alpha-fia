#bibliotecas Python
import pandas as pd
import datetime as dt

#Comunicação com sistema
from busca_dados import get_prices
from criterios_elegibilidade import criterios_elegibilidade
from formacao_carteiras import forma_carteiras
from fatores_risco import calcula_fatores_risco
from alpha import jensens_alpha
from matrixDB import get_tickers
from fundos_investimento import preprocess_fis

import util


def main():
	#Parâmetros escolhidos
	##Tempo
	start = "2010-01-01"
	end = dt.date.today()
	freq = "daily"

	##Liquidez
	liquidez_min = 0.1 #elimina 10% dos volumes mais baixos
	criterio_liquidez = 0.8 #liquidez em 80% dos períodos
	media_periodo = 21

	##Fonte
	get_from="yahoo"

	#parâmetros adicionais
	
	verbose = True
	persist = True
	test = False

	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("----------------------- INICIANDO PROCEDIMENTO DE BUSCA DE COTAÇÕES -----------------------")
		print("-------------------------------------------------------------------------------------------")

	#Algoritmo

	#### Busca preços de ações

	if True:
		tickers = list(pd.read_csv("./data/ticker_list.csv", index_col=0)["tickers"])
		prices = dict()
		for ticker in tickers:
			prices[ticker] = pd.read_csv("./data/prices/" + ticker + ".csv", index_col=0)
	else:
		tickers = "all"
		prices = get_prices(tickers, start, end, verbose, get_from)
		if persist:
			if verbose:
				print("-- Persistindo preços. Não interrompa a execução. --")
			pd.DataFrame({"tickers": list(prices.keys())}).to_csv("./data/ticker_list.csv")
			for ticker in prices.keys():
				prices[ticker].to_csv("./data/prices/" + ticker + ".csv")
			if verbose:
				print("-- OK --")

	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("---------------------  INICIANDO PROCEDIMENTO DE AVALIAÇÃO DA AMOSTRA ---------------------")
		print("-------------------------------------------------------------------------------------------")

	if test:
		amostra_aprovada = pd.read_csv("./data/criterios/amostra_aprovada.csv", index_col=0)		
	else:
		amostra_aprovada = criterios_elegibilidade(prices, start, end, freq, liquidez_min, criterio_liquidez, media_periodo, persist, verbose)
		if persist:
			amostra_aprovada.to_csv("./data/criterios/amostra_aprovada.csv")

	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("--------------------- INICIANDO PROCEDIMENTO DE FORMAÇÃO DE CARTEIRAS ---------------------")
		print("-------------------------------------------------------------------------------------------")
	#### Forma carteiras para cada período
	if test:
		carteiras = dict()
		carteiras["value"] = pd.read_csv("./data/carteiras/value.csv", index_col=0)
		carteiras["size"] = pd.read_csv("./data/carteiras/size.csv", index_col=0)
		carteiras["liquidity"] = pd.read_csv("./data/carteiras/liquidity.csv", index_col=0)
		carteiras["momentum"] = pd.read_csv("./data/carteiras/momentum.csv", index_col=0)
	else:
		carteiras = forma_carteiras(prices, amostra_aprovada, start, end, freq, verbose)
		if persist:
			if verbose:
				print("-- Persistindo carteiras --")
			for carteira in carteiras:
				carteiras[carteira].to_csv("./data/carteiras/"+ carteira +".csv")
			if verbose:
				print("OK")
	#### Calcula fatores de risco
	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("------------------ INICIANDO PROCEDIMENTO DE CÁLCULO DE FATORES DE RISCO ------------------")
		print("-------------------------------------------------------------------------------------------")

	if test:
		fatores_risco = pd.read_csv("./data/fatores/fatores_risco.csv", index_col=0)
	else:
		fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, verbose)
		if persist:
			if verbose:
				print("Persistindo fatores de risco")
			fatores_risco.to_csv("./data/fatores/fatores_risco.csv")
			if verbose:
				print("OK")
	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("------------------- INICIANDO PROCEDIMENTO DE CÁLCULO DO ALFA DE JENSEN -------------------")
		print("-------------------------------------------------------------------------------------------")

	fis = preprocess_fis(pd.read_csv("./data/cotas_fias.csv"))
	alphas = jensens_alpha(fatores_risco, fis, fatores=["fator_mercado","fator_tamanho","fator_valor","fator_liquidez","fator_momentum"],verbose=verbose)
	if persist:
		alphas.to_csv("./data/alphas/alphas.csv")


	if verbose:
		print("-------------------------------------------------------------------------------------------")
		print("---------------------------------------FIM-------------------------------------------------")
		print("-------------------------------------------------------------------------------------------")
	return


if __name__ == "__main__":
    main()