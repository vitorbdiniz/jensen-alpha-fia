USE TC_LABS_risk_factors;

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
    name VARCHAR(100) NOT NULL,
    
    PRIMARY KEY(id)
);

CREATE TABLE ticker_dimension(
	id INT NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    
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

CREATE TABLE risk_factors(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
    
    fator_mercado DOUBLE,
	fator_tamanho DOUBLE,
	fator_valor DOUBLE,
    fator_liquidez DOUBLE,
    fator_momentum DOUBLE,
    fator_bab DOUBLE,
    fator_qualidade DOUBLE,
    
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
ALTER TABLE risk_factors
	ADD CONSTRAINT risk_fk_time FOREIGN KEY (time_id)
		REFERENCES time_dimension(id)
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