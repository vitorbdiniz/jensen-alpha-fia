import pandas as pd
import datetime as dt

from busca_dados import get_prices
from criterios_elegibilidade import criterios_elegibilidade
from formacao_carteiras import forma_carteiras
from fatores_risco import calcula_fatores_risco

from matrixDB import get_tickers

def main():
	#Parâmetros escolhidos
	tickers = "all"
	start = "2010-01-01"
	end = dt.date.today()
	freq = "daily"
	liquidez_min = 0
	criterio_liquidez = 0.8
	verbose = True
	persist = True

	#Algoritmo
	prices = get_prices(tickers, start, end, verbose)
	amostra_aprovada = criterios_elegibilidade(prices, start, end, freq, liquidez_min, criterio_liquidez, verbose)
	if persist:
		amostra_aprovada.to_csv("amostra_aprovada.csv")
	carteiras = forma_carteiras(prices, amostra_aprovada, start, end, verbose)
	if persist:
		carteiras.to_csv("carteiras.csv")
	
	#fatores_risco = calcula_fatores_risco(prices, carteiras, start, end, verbose)
	#if persist:
		#fatores_risco.to_csv("fatores_risco.csv")


	return


if __name__ == "__main__":
    main()