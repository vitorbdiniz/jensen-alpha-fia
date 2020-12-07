select e.denominacao_social, d.codigo_cvm ,c.data_periodo,
		c.codigo_conta, c.descricao, c.valor_conta
from empresas as e, demonstrativos as d, contas as c
where e.company_id = d.company_id and d.demonstrativo_id = c.demonstrativo_id and
		e.situacao_registro = 'ATIVO' and d.status = 'ATIVO' and c.consolidado = 2 and
        c.codigo_cvm = ':cvm:'

order by c.data_periodo desc, c.codigo_conta