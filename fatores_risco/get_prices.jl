
module prices
    using DataFrames, CSV;    
    export getPrices;

    function getPrices(test = false) ::DataFrame
        if(!test)
            run(`python3 companies.py`);        
        end
        prices::DataFrame = CSV.read("../data/prices.csv", DataFrame);
        return prices;
    end

end