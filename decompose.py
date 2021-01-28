import pandas as pd 
import numpy as np

import util



def decompose_by_factors(coeficients, factors, verbose=0):
  result = pd.DataFrame(columns = ["alpha"] + [x for x in factors.columns])
  betas = coeficients[[x for x in coeficients.columns if x.split("_")[0] == "alpha" or x.split("_")[0] == "beta"]]

  fac_index_0 = factors.index.get_loc(betas.index[0], method="pad")
  i = 1
  for index in betas.index:
    if verbose == 5:
      print(str(i) + ". Decompondo retornos em fatores de " + str("COSMOS") + " para a data " + index + " ---- restam " +str(len(betas.index)-i))
      i+=1
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
        premium_avg = util.avg_return(fator[fator.columns[0]].iloc[fac_index_0 : fac_index+1])
        decomposition.append(premium_avg * betas[col].loc[index])
    result.loc[index] = decomposition
  return result


