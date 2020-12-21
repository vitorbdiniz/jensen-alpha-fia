SELECT  t.codigo_negociacao, d.data_referencia, d.release_date,
        qtd_acao_ordinaria_capital_integralizado AS ordinaria, 
        qtd_acao_preferencial_capital_integralizado AS preferencial, 
        qtd_total_acao_capital_integralizado AS total
FROM demonstrativos AS d JOIN tickers AS t ON t.codigo_cvm = d.codigo_cvm
ORDER BY d.codigo_cvm, t.codigo_negociacao, d.data_referencia
;
