CREATE PROCEDURE `pr_add_new_day` (IN mydate DATE)
BEGIN
	INSERT INTO risk_factors.time_dimension (date_, `year`, `month`, `day`) 
    VALUES(mydate, YEAR(mydate), MONTH(mydate), DAY(mydate));
END
