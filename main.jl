using DataFrames;


#include("./fatores_risco/risk_factors.jl");
include("./MySQL/mysql_access.jl");
include("./fatores_risco/get_prices.jl");
include("./pre-processing/data_pre_processing.jl");
using .DBAccess, .prices,.preprocessing;

function main()

    verbose::Bool = true;
    persist::Bool = true;
    #Consultas----

    ## Ações
    stocks  ::DataFrame = getStocks(verbose, persist);
    ## Tickers
    tickers ::DataFrame = getTickers(verbose, persist);
    return 0;
    killUnits!(tickers);    
    ## Cotações
    prices  ::DataFrame = getPrices(test, verbose, persist);
    ## Retornos
    returns ::DataFrame = calculateReturns(prices);

    
    r = riskFactors(true, true, true);
    println(first(r,100));
    
end


main();