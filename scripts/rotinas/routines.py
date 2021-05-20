#bibliotecas Python
import pandas as pd
import datetime as dt

from scripts.rotinas import factors
from scripts.util import util, padding as pad

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
	prices = factors.busca_cotacoes(start, end, verbose=verbose, get_from=source, persist=persist, test=test)

	#### Avaliação da amostra
	amostra_aprovada = factors.monta_amostras(prices, test, start, end, criterio_liquidez, verbose, persist)

	#### Formação de carteiras para cada período
	carteiras = factors.monta_carteiras(prices, amostra_aprovada, quantile, test, start, end, verbose, persist)

	#### Cálculo de fatores de risco
	fatores_risco = factors.monta_fatores(prices, carteiras, start, end, False, verbose, persist)

	pad.verbose("- FIM -", level=1, verbose=verbose)
	return fatores_risco




def single_factor_routine(start, end, source = "yahoo", quantile = 0.5,criterio_liquidez = 0.8,test = False,verbose = 0, persist = False):
	"""
		Calcula um único fator para o todo o período selecionado
		Rotina:
			1. Cálculo de preços
			2. Aprovação de amostras
			3. Montagem de carteiras
			4. Cálculo de fatores
	"""
	return
