from scripts.rotinas import routines
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
	source = "yahoo"

	quantile = 1/3 
	criterio_liquidez = 0.8 
	longshort = False

	test = True 
	verbose = 5
	persist = True

	if routine == "factors_complete":
		result = routines.factors_complete_routine(start, end, source = source, quantile = quantile, criterio_liquidez = criterio_liquidez, test = test, verbose = verbose, persist = persist)
	elif routine == 'single_factor' and factor_name is not None:
		result = routines.single_factor_routine(factor_name, start, end, source = source, quantile = quantile,criterio_liquidez =criterio_liquidez,longshort=longshort, test = test,verbose =verbose, persist = persist)
	else:
		raise AttributeError(f"Rotina incorreta. Valor de `routine` inserido foi '{routine}'")
	

	return result


if __name__ == "__main__":
	routine = "single_factor"
	result = main(routine, factor_name='SMB')
	print(result)