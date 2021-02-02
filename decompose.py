import pandas as pd 
import numpy as np
import datetime as dt

import util
import padding as pad


def decompose_all_by_factors(alphas, factors, verbose=0):
    return { 
      fund : decompose_fund_by_factors(alphas[fund], factors, fund, verbose=verbose) 
      for fund in alphas
      } 


def decompose_fund_by_factors(coeficients, factors, fund, verbose=0):
  pad.verbose("- Decompondo portfolio de "+str(fund.split(" ")[0])+" -", level=2, verbose=verbose)
  result = pd.DataFrame(columns = ["alpha"] + [x for x in factors.columns])
  betas = coeficients[[x for x in coeficients.columns if x.split("_")[0] == "alpha" or x.split("_")[0] == "beta"]]

  fac_index_0 = factors.index.get_loc(betas.index[0], method="pad")
  i = 1
  for index in betas.index:
    pad.verbose(str(i) + ". Decompondo retornos em fatores de " + str(fund) + " para a data " + str(index) + " ---- restam " +str(len(betas.index)-i), level=5, verbose=verbose)
    i+=1

    result.loc[index] = decompose_by_factors(betas, factors, index, fac_index_0)
  pad.verbose("line", level=3, verbose=verbose)
  return result

def decompose_by_factors(betas, factors, index, fac_index_0):
    decomposition = []
    for j in range(len(betas.columns)):
      col = betas.columns[j]
      if j == 0:
        decomposition.append(betas[col].loc[index])
      else:
        fac_index = factors.index.get_loc(index, method="pad")
        fator = factors[ 
                        [ "fator_"+x.split("_")[1] for x in betas.columns if len(x.split("_")) > 1 and x.split("_")[1]==col.split('_')[1] ] 
                        ]
        premium_avg = util.avg_return(fator[fator.columns[0]].iloc[fac_index_0 : fac_index+1].tolist())
        try:
            decomposition.append(float(premium_avg * betas[col].loc[index]))
        except:
            print("Premium: ", premium_avg, type(premium_avg))
            print("Beta "+str(col)+": ", betas[col].loc[index], type(betas[col].loc[index]))
            exit(1)
    return decomposition
		
    