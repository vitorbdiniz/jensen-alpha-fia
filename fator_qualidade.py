import pandas as pd
import datetime as dt
from scipy.stats import zscore


def carteiraQuality(prices, amostra_aprovada, quantile, start= dt.date.today(), end= dt.date.today(), verbose=False):
    '''
        Classifica cada ativo por período (diário, trimestral ou anual) em "quality" ou "junk" de acordo com ... (Ver Buffett's Alpha)
    '''

    # Profitability = z (z_gpoa + zroe + zroa + zcfoa + zgmar + zacc) 
    # Growth = z (zΔgpoa + zΔroe + zΔroa + zΔcfoa + zΔgmar)
    # Safety = z(zbab + zlev + zo + zz + zevol)
    # Quality = z (Profitabiliy + Growth + Safety)



    #TODO
    return

def z(array):
    '''
        Z-Score a partir do método de Clifford S. Asness 1 & Andrea Frazzini & Lasse Heje Pedersen
        Consiste em calcular o z-score do array (utilizando scipy) e calcular a média dos z-scores
        retorna 
    '''

