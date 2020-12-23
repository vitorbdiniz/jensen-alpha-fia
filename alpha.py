import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import statistics as st
import datetime as dt
import util



def jensens_alpha(risk_factors, portfolio_returns):
    pricing_model = LinearRegression().fit(risk_factors, portfolio_returns)
    return pricing_model

