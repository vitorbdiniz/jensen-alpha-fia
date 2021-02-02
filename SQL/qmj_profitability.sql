SELECT indicadores_qmj.codigo_cvm, indicadores_qmj.ticker, indicadores_qmj.data_referencia, indicadores_qmj.demonstrativo_id, contas_qmj.nome_demonstrativo,
contas_qmj.ativos, contas_qmj.receita, contas_qmj.custos, 
indicadores_qmj.ROE, indicadores_qmj.ROA, indicadores_qmj.depreciacao, indicadores_qmj.wc, indicadores_qmj.capex
FROM (
		SELECT C.codigo_cvm AS codigo_cvm, C.demonstrativo_id AS demonstrativo_id,C.nome_demonstrativo AS nome_demonstrativo, C.data_periodo AS data_periodo, 
				C.valor_conta AS custos, RL.valor_conta AS receita, A.valor_conta AS ativos
		FROM (

		#TABELA CONTAS 
			(
				#CUSTOS
				SELECT contas.codigo_cvm, contas.demonstrativo_id,nome_demonstrativo,contas.data_periodo, contas.valor_conta
				FROM contas
				WHERE contas.codigo_conta = 3.02 AND contas.consolidado=2

			) AS C JOIN (

						#RECEITA LÍQUIDA
						SELECT codigo_cvm, demonstrativo_id,nome_demonstrativo, data_periodo, valor_conta
						FROM contas
						WHERE codigo_conta = "3.01" AND consolidado=2

						) AS RL
			ON C.demonstrativo_id = RL.demonstrativo_id
		) JOIN (

				#ATIVOS TOTAIS
				SELECT codigo_cvm, demonstrativo_id,nome_demonstrativo, data_periodo, valor_conta
				FROM contas
				WHERE codigo_conta = 1 AND consolidado=2

		) AS A ON A.demonstrativo_id = C.demonstrativo_id 
	ORDER BY C.codigo_cvm, C.data_periodo
) AS contas_qmj

JOIN (

		SELECT roe.num,roe.codigo_cvm, roe.ticker, roe.data_referencia, roe.demonstrativo_id,
				roe.valor AS ROE, roa.valor AS ROA, dna.valor AS depreciacao, wc.valor AS wc, cx.valor AS capex
		FROM (# roe JOIN roa JOIN d&a JOIN wc JOIN capex
		((
			(
				#ROE
				SELECT ROW_NUMBER() OVER (ORDER BY codigo_cvm, data_referencia) AS num, codigo_cvm, ticker, data_referencia, demonstrativo_id,indicador, valor
				FROM indicadores
				WHERE consolidado = 2  AND indicador="ROE"
				ORDER BY codigo_cvm, demonstrativo_id
			) AS roe JOIN (
				#ROA
				SELECT ROW_NUMBER() OVER (ORDER BY codigo_cvm, data_referencia) AS num, codigo_cvm, ticker, data_referencia, demonstrativo_id,indicador, valor
				FROM indicadores
				WHERE consolidado = 2  AND
				indicador="ROA"
				ORDER BY codigo_cvm, data_referencia
			) AS roa ON roe.num=roa.num
		) JOIN (
				#D&A
				SELECT ROW_NUMBER() OVER (ORDER BY codigo_cvm, data_referencia) AS num, codigo_cvm, ticker, data_referencia, demonstrativo_id, valor
				FROM indicadores
				WHERE consolidado = 2 AND
				indicador="(+) Depreciação e Amortização" #IN ("ROE", "ROA", "(+) Depreciação e Amortização", '(-) Investimento em Capital de Giro Líquido')

				) AS dna ON dna.num=roe.num
		) JOIN (
				#WC
				SELECT ROW_NUMBER() OVER (ORDER BY codigo_cvm, data_referencia) AS num, codigo_cvm, ticker, data_referencia, demonstrativo_id, valor
				FROM indicadores
				WHERE consolidado = 2 AND
				indicador="(-) Investimento em Capital de Giro Líquido"
		) AS wc ON wc.num = roe.num
		) JOIN (
				SELECT ROW_NUMBER() OVER (ORDER BY codigo_cvm, data_referencia) AS num, codigo_cvm, ticker, data_referencia, demonstrativo_id, valor
				FROM indicadores
				WHERE consolidado = 2 AND indicador='(-) CAPEX'
				ORDER BY codigo_cvm, data_referencia
		) AS cx ON cx.num=roe.num

		ORDER BY roe.codigo_cvm, roe.data_referencia

) AS indicadores_qmj

ON indicadores_qmj.demonstrativo_id=contas_qmj.demonstrativo_id

ORDER BY indicadores_qmj.codigo_cvm, indicadores_qmj.data_referencia;
