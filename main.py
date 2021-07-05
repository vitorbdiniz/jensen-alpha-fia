from scripts.rotinas import routines
from scripts.data.busca_dados import get_prices
from datetime import date

def main(routine = "factors_complete", factor_name=None):
	"""
		A função main executará a rotina solicitada
		lista de rotinas:
			1. 'factors_complete' -> Calcula todos os 7 fatores para o período de 2010-01-01 até hoje
			2. 'factors_update' -> TODO
			3. 'alpha_complete' -> TODO
			4. 'alpha_onedate' -> TODO
			4. 'alpha_singleportfolio_complete' -> TODO
			5. 'alpha_singleportfolio_onedate' -> TODO
	"""
	start = date(2010, 1, 1)
	end = date.today()
	source = "tc"

	quantile = 1/3 
	criterio_liquidez = 0.8 
	longshort = True

	test = False
	verbose = 5
	persist = True

	if routine == "factors_complete":
		result = routines.factors_complete_routine(start, end, source = source, quantile = quantile, criterio_liquidez = criterio_liquidez, test = test, verbose = verbose, persist = persist)
	elif routine == 'single_factor' and factor_name is not None:
		result = routines.single_factor_routine(factor_name, start, end, source = source, quantile = quantile,criterio_liquidez =criterio_liquidez, test = test,verbose =verbose, persist = persist)
	elif routine == 'prices':
		result = get_prices(['PETR4'], start='2010-01-01')
	
	else:
		raise AttributeError(f"Rotina incorreta. Valor de `routine` inserido foi '{routine}'")
	
	return result

if __name__ == "__main__":
	routine = "factors_complete"
	result = main(routine, 'MKT')
	print(result)