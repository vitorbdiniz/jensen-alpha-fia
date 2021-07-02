SELECT *
FROM prices
WHERE  	date_ >= :start_date: AND date_ <= :end_date:
		AND ticker IN :ticker_tuple:
ORDER BY ticker_id ASC, time_id ASC
;