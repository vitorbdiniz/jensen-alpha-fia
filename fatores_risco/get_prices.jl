
module prices
    using DataFrames, CSV;    
    include("../utils.jl");
    using .utils;

    export getPrices;

    function getPrices(test::Bool = false, verbose::Bool=false, persist::Bool=false) ::DataFrame
        verboseMessage(verbose, "Buscando cotações");
        if(!test)
            run(`python3 ./fatores_risco/companies.py`);        
        end
        prices::DataFrame = CSV.read("./data/prices.csv", DataFrame);
        persistDataFrame(prices, "./data/prices.csv", persist);

        return prices;
    end

end