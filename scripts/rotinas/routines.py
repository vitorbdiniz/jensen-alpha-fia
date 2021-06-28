#bibliotecas Python
import pandas as pd
import datetime as dt

from scripts.rotinas import factors
from scripts.fatores.fatores_risco import marketFactor
from scripts.util import util, padding as pad

#Comunicação com sistema
from scripts.data.busca_dados import get_prices
from scripts.data.criterios_elegibilidade import criterios_elegibilidade

from scripts.carteiras.formacao_carteiras import forma_carteiras
from scripts.fatores.fatores_risco import calcula_fatores_risco




def factors_complete_routine(start, end, source = "yahoo", quantile = 0.5,criterio_liquidez = 0.8, test = False,verbose = 0,persist = False):
	"""
		Calcula todos os fatores para o todo o período selecionado
		Rotina:
			1. Cálculo de preços
			2. Aprovação de amostras
			3. Montagem de carteiras
			4. Cálculo de fatores

		Parâmetros:
			start: {str or datetime.date} data de inicio
			end: {str or datetime.date} data final
			source = {'yahoo', 'TC'} fonte de onde provém os dados de cotações
			quantile = {float n, 0 < n <= 0.5} quantil base para montagem de carteiras
			criterio_liquidez = {float n, 0 < n <= 1} fração do numero de dias de liquidez minima por ano
			test = {boolean} caso True, realiza código de teste
			verbose = {int n, 0 <= n <= 5} nível de verbose
			persist = {boolean} caso True, persiste dados
	"""

	#### Busca de preços de ações
	prices = factors.busca_cotacoes(start, end, verbose=verbose, test=test)
	pad.persist_collection(prices, path="./data/prices/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo preços. Não interrompa a execução. -")

	#### Avaliação da amostra
	amostra_aprovada = factors.monta_amostras(prices, start, end, criterio_liquidez=criterio_liquidez, verbose=verbose, test=test)
	pad.persist(amostra_aprovada, path="./data/criterios/amostra_aprovada.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo amostra avaliada. Não interrompa a execução. -")
	
	#### Formação de carteiras para cada período
	carteiras = factors.monta_carteiras(prices, amostra_aprovada, quantile, start, end, verbose=verbose, test=test)
	pad.persist_collection(carteiras, path="./data/carteiras/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo carteiras. Não interrompa a execução. -")
	
	#### Cálculo de fatores de risco
	fatores_risco = factors.monta_fatores(prices, carteiras, start, end, verbose=verbose, test=test)
	if type(fatores_risco) == dict:
		pad.persist_collection(fatores_risco, path="./data/fatores/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo fatores de risco. Não interrompa a execução. -")
	else:
		pad.persist(fatores_risco, path="./data/fatores/fatores_risco.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo fatores de risco. Não interrompa a execução. -")

	pad.verbose("- FIM -", level=1, verbose=verbose)
	return fatores_risco




def single_factor_routine(factor, start, end, source = "yahoo", quantile = 0.5,criterio_liquidez = 0.8, test = False,verbose = 0, persist = False):
	"""
		Calcula um único fator para o todo o período selecionado.
		Rotina:
			1. Cálculo de preços
			2. Aprovação de amostras
			3. Montagem de carteiras
			4. Cálculo de fatores
		
		Parâmetros:
			factor: {'MKT', 'SMB', 'HML', 'IML', 'WML', 'BAB'} Nome do fator
			start: {str or datetime.date} data de inicio
			end: {str or datetime.date} data final
			source = {'yahoo', 'TC'} fonte de onde provém os dados de cotações, apenas se factor != 'MKT'
			quantile = {float n, 0 < n <= 0.5} quantil base para montagem de carteiras, apenas se factor != 'MKT'
			criterio_liquidez = {float n, 0 < n <= 1} fração do numero de dias de liquidez minima por ano, apenas se factor != 'MKT'
			test = {boolean} caso True, realiza código de teste, apenas se factor != 'MKT'
			verbose = {int n, 0 <= n <= 5} nível de verbose
			persist = {boolean} caso True, persiste dados
	"""

	if factor != 'MKT':
		#### Busca de preços de ações
		prices = get_prices(start=start, end=end, verbose=verbose)
		pad.persist_collection(prices, path="./data/prices/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo preços. Não interrompa a execução. -")

		#### Avaliação da amostra
		amostra_aprovada = criterios_elegibilidade(prices, start = start, end = end, criterion = criterio_liquidez, verbose = verbose)
		pad.persist(amostra_aprovada, path="./data/criterios/amostra_aprovada.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo amostra avaliada. Não interrompa a execução. -")
		
		#### Formação de carteiras para cada período
		carteiras = forma_carteiras(prices, amostra_aprovada, quantile, start, end, verbose)
		pad.persist_collection(carteiras, path="./data/carteiras/", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo carteiras. Não interrompa a execução. -")	

		#### Cálculo de fatores de risco
		fatores_risco = calcula_fatores_risco(prices, carteiras, start=start, end=end, fatores_desejados=factor, verbose=verbose)
	else:
		fatores_risco = calcula_fatores_risco(start = start, end=end, fatores_desejados=factor, verbose=verbose)

	fatores_risco = fatores_risco[factor]
	pad.persist(fatores_risco, path=f"./data/fatores/{factor}.csv", to_persist=persist, _verbose=verbose, verbose_level=2, verbose_str="- Persistindo fatores de risco. Não interrompa a execução. -")

	pad.verbose("- FIM -", level=1, verbose=verbose)
	return fatores_risco


