USE risk_factors;

#basic dimensions
CREATE TABLE time_dimension(
	id INT NOT NULL AUTO_INCREMENT,
    date_ date,
    year INT,
    month INT,
    day INT,
    
    PRIMARY KEY(id)
);



CREATE TABLE funds_dimension(
	id INT NOT NULL,
    name VARCHAR2(100) NOT NULL,
    
    PRIMARY KEY(id)
);

CREATE TABLE ticker_dimension(
	id INT NOT NULL AUTO_INCREMENT,
    ticker VARCHAR(10) NOT NULL,
	exchange VARCHAR(30) NOT NULL,
    
    PRIMARY KEY(id)
);

# Other Dimensions
CREATE TABLE prices(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	ticker_id INT NOT NULL,
    
    high FLOAT,
    low FLOAT,
	open FLOAT,
	close FLOAT,
    volume FLOAT,
    adj_close FLOAT,
    
    PRIMARY KEY(id)
);

#Risk factors
##Fact Table
CREATE TABLE risk_factors_fact(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
    
    market_factor_id INT NOT NULL,
	size_factor_id INT NOT NULL,
	value_factor_id INT NOT NULL,
    illiquidity_factor_id INT NOT NULL,
    momentum_factor_id INT NOT NULL,
    betting_against_beta_factor_id INT NOT NULL,
    quality_factor_id INT NOT NULL,
    
    PRIMARY KEY(id)
);

CREATE TABLE market_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	market_return DOUBLE,
    risk_free DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);

CREATE TABLE size_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);


CREATE TABLE value_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
    long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);

CREATE TABLE momentum_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);


CREATE TABLE illiquidity_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);

CREATE TABLE betting_against_beta_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);
CREATE TABLE quality_factor(
	id INT NOT NULL AUTO_INCREMENT,
    time_id INT NOT NULL,
	long_portfolio_value DOUBLE,
    short_portfolio_value DOUBLE,
    risk_factor_value DOUBLE,
    
    PRIMARY KEY(id)
);

CREATE TABLE criteria(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	ticker_id INT NOT NULL,
    
    liquidez_minima BOOLEAN,
    listagem BOOLEAN,
    maior_liquidez BOOLEAN,

    PRIMARY KEY(id)
);

CREATE TABLE carteiras(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	ticker_id INT NOT NULL,
    
    carteira_tamanho VARCHAR(15),
    carteira_valor VARCHAR(15),
    carteira_liquidez VARCHAR(15),
    carteira_momentum VARCHAR(15),
    carteira_beta VARCHAR(15),
	carteira_qualidade VARCHAR(15),

    PRIMARY KEY(id)
);

CREATE TABLE funds_performances(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	fund_id INT NOT NULL,

    quote DOUBLE NOT NULL,
    variation DOUBLE NOT NULL,
    captation DOUBLE NOT NULL,
    equity DOUBLE NOT NULL,
    investors INT NOT NULL,
	withdraws DOUBLE NOT NULL,

	PRIMARY KEY(id)
);

CREATE TABLE alphas(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
    fund_id INT NOT NULL,

    alpha DOUBLE NOT NULL,    
    beta_mercado DOUBLE,
    beta_tamanho DOUBLE,	
    beta_valor DOUBLE,
    beta_liquidez DOUBLE,
    beta_momentum DOUBLE,
    beta_BAB DOUBLE,
    beta_quality DOUBLE,

	PRIMARY KEY(id)
);

CREATE TABLE regression_statistics(
	id INT NOT NULL AUTO_INCREMENT,
    alpha_id INT NOT NULL,
    
	tvalue_alpha DOUBLE NOT NULL,
    tvalue_mercado DOUBLE NOT NULL,	
    tvalue_tamanho DOUBLE NOT NULL,
    tvalue_valor DOUBLE NOT NULL,
    tvalue_liquidez DOUBLE NOT NULL,
    tvalue_momentum DOUBLE NOT NULL,
    tvalue_beta DOUBLE NOT NULL,
    
    pvalue_alpha DOUBLE NOT NULL,
    pvalue_mercado DOUBLE NOT NULL,
    pvalue_tamanho DOUBLE NOT NULL,
    pvalue_valor DOUBLE NOT NULL,
    pvalue_liquidez DOUBLE NOT NULL,
    pvalue_momentum DOUBLE NOT NULL,
    pvalue_beta	DOUBLE NOT NULL,
    
    fvalue DOUBLE NOT NULL,
    f_pvalue DOUBLE NOT NULL,
    R_squared_adj DOUBLE NOT NULL,

	PRIMARY KEY(id)
);

#Table Relations

ALTER TABLE prices
	ADD CONSTRAINT prices_fk_ticker FOREIGN KEY (ticker_id)
		REFERENCES ticker_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT prices_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE quality_factor
	ADD CONSTRAINT qmj_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE betting_against_beta_factor
	ADD CONSTRAINT bab_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE momentum_factor
	ADD CONSTRAINT wml_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE illiquidity_factor
	ADD CONSTRAINT iml_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE value_factor
	ADD CONSTRAINT hml_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE size_factor
	ADD CONSTRAINT smb_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE market_factor
	ADD CONSTRAINT mkt_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE risk_factors_fact
	ADD CONSTRAINT risk_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_mkt FOREIGN KEY(market_factor_id)
		REFERENCES market_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_smb FOREIGN KEY(size_factor_id)
		REFERENCES size_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_hml FOREIGN KEY(value_factor_id)
		REFERENCES value_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_iml FOREIGN KEY(illiquidity_factor_id)
		REFERENCES illiquidity_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_wml FOREIGN KEY(momentum_factor_id)
		REFERENCES momentum_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_bab FOREIGN KEY(betting_against_beta_factor_id)
		REFERENCES betting_against_beta_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT risk_fk_qmj FOREIGN KEY(quality_factor_id)
		REFERENCES quality_factor(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;



        
ALTER TABLE criteria
	ADD CONSTRAINT criteria_fk_ticker FOREIGN KEY (ticker_id)
		REFERENCES ticker_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT criteria_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE carteiras
	ADD CONSTRAINT carteiras_fk_ticker FOREIGN KEY (ticker_id)
		REFERENCES ticker_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT carteiras_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE funds_performances
	ADD CONSTRAINT performance_fk_fund FOREIGN KEY (fund_id)
		REFERENCES funds_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT performance_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE alphas
	ADD CONSTRAINT alpha_fk_fund FOREIGN KEY (fund_id)
		REFERENCES funds_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	ADD CONSTRAINT alpha_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;
ALTER TABLE regression_statistics
	ADD CONSTRAINT regr_fk_alpha FOREIGN KEY (alpha_id)
		REFERENCES alphas(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;