module factors
    #Libs----
    using DataFrames, CSV, Dates;

    #My Modules----
    include("../MySQL/mysql_access.jl");
    include("./get_prices.jl");
    using .DBAccess, .prices;

    #Export functions----
    export riskFactors;



    #Functions----

    function riskFactors(test::Bool = false)
        #Cálculo dos fatores de risco em base diária

        #Consultas
        tickers ::DataFrame = getTickers();
        prices  ::DataFrame = getPrices(test);
        stocks  ::DataFrame = getStocks();

        #Processamento de dados
        returns ::DataFrame = calculateReturns(prices);

        calculatedFactors ::DataFrame = calculateRiskFactors(returns, stocks);
#        CSV.write("../data/riskFactors.csv", calculatedFactors);
        return calculatedFactors;
    end



    function calculateRiskFactors(returns::DataFrame, stocks::DataFrame)::DataFrame
        #Cálculo dos fatores de risco
        size::DataFrame = sizeFactor(returns, stocks);
        value::DataFrame = valueFactor(returns, stocks);
        liquidity::DataFrame = liquidityFactor(returns);
        momentum::DataFrame = momentumFactor(returns);
        market::DataFrame = marketFactor(returns);

        return appendDataFrames(size, value, liquidity, momentum, market);
    end

    function sizeFactor(returns::DataFrame, stocks::DataFrame) ::DataFrame
        #TODO

    end
    function valueFactor(returns::DataFrame, stocks::DataFrame) ::DataFrame
        #TODO

    end
    function liquidityFactor(returns ::DataFrame)::DataFrame
        #TODO    
    end
    function momentumFactor(returns ::DataFrame) ::DataFrame
        #TODO
    end
    function marketFactor(returns ::DataFrame)::DataFrame
        #TODO    
        #Necessita portfolio
    end


    #Util Functions
    function appendDataFrames(size::DataFrame, value::DataFrame, liquidity::DataFrame, momentum::DataFrame, market::DataFrame) ::DataFrame
        #Realiza a junção de todos os dataframes de fatores de risco
        result ::DataFrame;
        append!(result, market);
        append!(result, size);
        append!(result, value);
        append!(result, liquidity);
        append!(result, momentum);
        return result;
    end

    function calculateReturns(prices::DataFrame)
        #Calcula retornos diários
        ret::Array{Float64, 1} = [];
        for i in 2:nrow(prices)
            append!(ret, prices."Adj Close"[i]/prices."Adj Close"[i-1]-1);
        end
        delete!(prices, 1);
        return DataFrame(codigo_cvm = prices."codigo_cvm", ticker_id = prices."ticker_id",data=prices."date",retornos = ret, volume = prices."Volume");
    end

end
