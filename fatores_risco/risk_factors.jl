#Libs
using DataFrames, CSV, Dates;

#My Modules
include("../MySQL/mysql_access.jl");
include("./get_prices.jl");
using .DBAccess, .pandas_datareader;

#Functions

function riskFactors()
    tickers ::DataFrame = getTickers();
    CSV.write("../data/tickers.csv", tickers);
    prices::DataFrame = getPrices(tickers);
#    factors::DataFrame = calculateRiskFactors(prices);
#    CSV.write("../data/riskFactors.csv", factors);
#    return factors;
end


function calculateRiskFactors(prices::DataFrame)::DataFrame
    size::DataFrame = sizeFactor(prices);
    value::DataFrame = valueFactor(prices);
    liquidity::DataFrame = liquidityFactor(prices);
    momentum::DataFrame = momentumFactor(prices);
    market::DataFrame = marketFactor(prices);

    resultRiskFactors ::DataFrame = appendDataFrames(size, value, liquidity, momentum, market);
    return resultRiskFactors;
end

function sizeFactor(prices::DataFrame) ::DataFrame
    #TODO

end
function valueFactor(prices::DataFrame) ::DataFrame
    #TODO
    
end
function liquidityFactor(prices ::DataFrame)::DataFrame
    #TODO    
end
function momentumFactor(prices ::DataFrame) ::DataFrame
    #TODO
end
function marketFactor(prices ::DataFrame)::DataFrame
    #TODO    
    #Necessita portfolio
end

function appendDataFrames(size::DataFrame, value::DataFrame, liquidity::DataFrame, momentum::DataFrame, market::DataFrame) ::DataFrame
    result ::DataFrame;
    append!(result, market);
    append!(result, size);
    append!(result, value);
    append!(result, liquidity);
    append!(result, momentum);
    return result;
end

riskFactors();
