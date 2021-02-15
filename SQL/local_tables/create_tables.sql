#basic dimensions
CREATE TABLE time_dimension(
	id INT NOT NULL AUTO_INCREMENT,
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

# Dimensions

CREATE TABLE prices(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	ticker_id VARCHAR(8) NOT NULL,
    
    high FLOAT,
    low FLOAT,
	open FLOAT,
	close FLOAT,
    volume FLOAT,
    adj_close FLOAT,
    liquid_days FLOAT,
    
    PRIMARY KEY(id),
    FOREIGN KEY(time_id) 
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(ticker_id) 
		REFERENCES ticker_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    
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
    
    PRIMARY KEY(id),
    FOREIGN KEY(time_id) 
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);

CREATE TABLE criteria(
	id INT NOT NULL AUTO_INCREMENT,
	time_id INT NOT NULL,
	ticker_id INT NOT NULL,
    
    liquidez_minima BOOLEAN,
    listagem BOOLEAN,
    maior_liquidez BOOLEAN,

    PRIMARY KEY(id),
    FOREIGN KEY(time_id) 
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(ticker_id) 
		REFERENCES ticker_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
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

    PRIMARY KEY(id),
    FOREIGN KEY(time_id) 
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(ticker_id) 
		REFERENCES ticker_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
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

	PRIMARY KEY(id),
	FOREIGN KEY(time_id)
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(fund_id) 
		REFERENCES funds_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
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

	PRIMARY KEY(id),
	FOREIGN KEY(time_id) 
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(fund_id) 
		REFERENCES funds_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE regression_statistics(
	id INT NOT NULL AUTO_INCREMENT,
    fund_id INT NOT NULL,
    time_id INT NOT NULL,
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

	PRIMARY KEY(id),
	FOREIGN KEY(time_id)
		REFERENCES time_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(fund_id) 
		REFERENCES funds_dimension(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY(alpha_id) 
		REFERENCES alphas(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);




