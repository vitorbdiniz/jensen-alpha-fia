SELECT equity.codigo_negociacao,equity.codigo_cvm, equity.demonstrativo_id, equity.codigo_conta,equity.data_periodo, d.release_date, qtd_acao_ordinaria_capital_integralizado AS ordinaria, qtd_acao_preferencial_capital_integralizado AS preferencial, qtd_total_acao_capital_integralizado AS total, equity.valor_conta, equity.valor_conta/qtd_total_acao_capital_integralizado AS VPA
FROM demonstrativos AS d JOIN(
	SELECT t.codigo_negociacao,c.codigo_cvm, c.demonstrativo_id, c.codigo_conta,c.data_periodo, c.valor_conta
	FROM contas AS c 
			JOIN empresas AS e ON c.codigo_cvm = e.codigo_cvm
			JOIN tickers AS t ON c.codigo_cvm = t.codigo_cvm
	WHERE 	c.consolidado = 2 AND 
			c.codigo_conta = "2.03" AND
			e.tc_codigo_setor != 2


	UNION 

	SELECT t.codigo_negociacao,c.codigo_cvm, c.demonstrativo_id, c.codigo_conta,c.data_periodo, c.valor_conta
	FROM contas AS c 
			JOIN empresas AS e ON c.codigo_cvm = e.codigo_cvm
			JOIN tickers AS t ON c.codigo_cvm = t.codigo_cvm
	WHERE 	c.consolidado = 2 AND 
			c.codigo_conta = "2.08" AND
			e.tc_codigo_setor = 2
	) AS equity
    ON equity.demonstrativo_id=d.demonstrativo_id
ORDER BY equity.codigo_cvm,equity.codigo_negociacao, equity.data_periodo
;