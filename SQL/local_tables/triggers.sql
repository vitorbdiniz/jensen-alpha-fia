delimiter $$
CREATE TRIGGER tr_insert_risk_factors BEFORE INSERT ON risk_factors
FOR EACH ROW
BEGIN
	SET NEW.time_id = func_get_time_id(NEW.date_);
    SET NEW.factor_name = func_get_risk_factor_name(NEW.factor_symbol);    
END;$$
delimiter ;


delimiter $$
CREATE TRIGGER tr_insert_prices BEFORE INSERT ON prices
FOR EACH ROW
BEGIN
	SET NEW.time_id = func_get_time_id(NEW.date_);
    SET NEW.ticker_id = func_get_ticker_id(NEW.ticker);
END;$$
delimiter ;


delimiter $$
CREATE TRIGGER tr_insert_portfolios BEFORE INSERT ON portfolios
FOR EACH ROW
BEGIN
	SET NEW.time_id = func_get_time_id(NEW.date_);
    SET NEW.ticker_id = func_get_ticker_id(NEW.ticker);
END;$$
delimiter ;



delimiter $$
CREATE TRIGGER tr_insert_criteria BEFORE INSERT ON criteria
FOR EACH ROW
BEGIN
	SET NEW.time_id = func_get_time_id(NEW.date_);
    SET NEW.ticker_id = func_get_ticker_id(NEW.ticker);
END;$$
delimiter ;
