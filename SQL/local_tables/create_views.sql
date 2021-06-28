CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `market_factor` AS
    SELECT 
        `risk_factors`.`id` AS `id`,
        `risk_factors`.`time_id` AS `time_id`,
        `risk_factors`.`long_portfolio_value` AS `market_returns`,
        `risk_factors`.`short_portfolio_value` AS `risk_free`,
        `risk_factors`.`risk_factor_value` AS `mkt_factor`
    FROM
        `risk_factors`
    WHERE
        (`risk_factors`.`factor_symbol` = 'MKT')
;