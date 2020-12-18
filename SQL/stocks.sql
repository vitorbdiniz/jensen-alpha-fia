SELECT d.codigo_cvm AS codigo_cvm,ticker_id, codigo_negociacao, data_referencia,qtd_acao_ordinaria_capital_integralizado AS ordinarias, qtd_acao_preferencial_capital_integralizado AS preferenciais, qtd_total_acao_capital_integralizado AS totais
FROM tc_matrix.tickers AS t, demonstrativos AS d
WHERE t.codigo_cvm = d.codigo_cvm
ORDER BY codigo_cvm, ticker_id, data_referencia
;