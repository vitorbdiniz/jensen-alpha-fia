import pandas as pd
import datetime as dt

from busca_dados import get_prices
from criterios_elegibilidade import criterios_elegibilidade
from formacao_carteiras import forma_carteiras
from fatores_risco import calcula_fatores_risco
from alpha import jensens_alpha
from matrixDB import get_tickers

import util


def main():
	#Parâmetros escolhidos
	start = "2010-01-01"
	end = dt.date.today()
	freq = "daily"
	liquidez_min = 0
	criterio_liquidez = 0.8
	#parâmetros adicionais
	verbose = True
	persist = True
	test = True

	#Algoritmo

	#### Busca preços de ações

	if test:
		tickers = list(pd.read_csv("./data/ticker_list.csv", index_col=0)["tickers"])
		prices = dict()
		for ticker in tickers:
			prices[ticker] = pd.read_csv("./data/prices/" + ticker + ".csv", index_col=0)
	else:
		tickers = "all"
		prices = get_prices(tickers, start, end, verbose)
		if persist:
			if verbose:
				print("-- Persistindo preços. Não interrompa a execução. --")
			pd.DataFrame({"tickers": list(prices.keys())}).to_csv("./data/ticker_list.csv")
			for ticker in prices.keys():
				prices[ticker].to_csv("./data/prices/" + ticker + ".csv")
			if verbose:
				print("-- OK --")

	#### Avalia amostra de preços
	if test:
		amostra_aprovada = pd.read_csv("./data/amostra_aprovada.csv", index_col=0)		
	else:
		amostra_aprovada = criterios_elegibilidade(prices, start, end, freq, liquidez_min, criterio_liquidez, verbose)
		if persist:
			amostra_aprovada.to_csv("./data/amostra_aprovada.csv")

	#### Forma carteiras para cada período
	if test:
		carteiras = dict()
		carteiras["value"] = pd.read_csv("./data/carteiras/value.csv", index_col=0)
		carteiras["size"] = pd.read_csv("./data/carteiras/size.csv", index_col=0)
		carteiras["liquidity"] = pd.read_csv("./data/carteiras/liquidity.csv", index_col=0)
		carteiras["momentum"] = pd.read_csv("./data/carteiras/momentum.csv", index_col=0)
	else:
		carteiras = forma_carteiras(prices, amostra_aprovada, start, end, freq, verbose, persist)

	#### Calcula fatores de risco
	fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, verbose)
	if persist:
		fatores_risco.to_csv("./data/fatores_risco.csv")

	#fias_returns = pd.read_csv("./data/cotas_fias.csv")
	#alpha = jensens_alpha(fatores_risco, fias_returns)
	
	return


if __name__ == "__main__":
    main()