
module prices
    using DataFrames, CSV;    
    export getPrices;

    function getPrices(tickers) ::DataFrame
        run(`python3 companies.py`);
        prices::DataFrame = CSV.read("../data/prices.csv", DataFrame);
        return prices;
    end

end