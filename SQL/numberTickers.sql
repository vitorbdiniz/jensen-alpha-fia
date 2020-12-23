SELECT codigo_cvm, count(codigo_cvm) AS quantity
FROM tickers
GROUP BY codigo_cvm
ORDER BY count(codigo_cvm) desc
;