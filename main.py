from scripts.rotinas import routines
from datetime import date

def main(routine = "factors_complete"):
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
	if routine == "factors_complete":
		routines.factors_complete_routine(start=date(2010, 1, 1), end=date.today(), source = "yahoo", quantile = 1/3, criterio_liquidez = 0.8, test = False, verbose = 5, persist = True)
	else:
		raise AttributeError("Rotina incorreta")
	return


if __name__ == "__main__":
    main()
