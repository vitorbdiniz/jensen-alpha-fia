SELECT t.codigo_negociacao,c.codigo_cvm, c.data_periodo, c.valor_conta
FROM contas AS c 
		JOIN empresas AS e ON c.codigo_cvm = e.codigo_cvm
        JOIN tickers AS t ON c.codigo_cvm = t.codigo_cvm
WHERE 	c.consolidado = 2 AND 
		c.codigo_conta = "2.03" AND
        e.tc_codigo_setor != 2


UNION 

SELECT t.codigo_negociacao,c.codigo_cvm, c.data_periodo, c.valor_conta
FROM contas AS c 
		JOIN empresas AS e ON c.codigo_cvm = e.codigo_cvm
        JOIN tickers AS t ON c.codigo_cvm = t.codigo_cvm
WHERE 	c.consolidado = 2 AND 
		c.codigo_conta = "2.08" AND
        e.tc_codigo_setor = 2
        

;