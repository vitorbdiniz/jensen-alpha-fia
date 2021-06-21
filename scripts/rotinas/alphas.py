import pandas as pd

from scripts.alpha.fundos_investimento import preprocess_fis
from scripts.alpha.decompose import decompose_all_by_factors
from scripts.alpha.alpha import jensens_alpha
from scripts.util import util, padding as pad

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

