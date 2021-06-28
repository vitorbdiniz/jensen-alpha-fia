CREATE FUNCTION `func_new_date` (year INT, month INT, day INT) RETURNS DATE
BEGIN
	SET str_date = CONCAT(year, '-', month, '-', day);
	RETURN CAST(str_date AS DATE);
END;
