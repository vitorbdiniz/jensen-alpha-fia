module factors
    #Libs----
    using DataFrames, CSV, Dates, Statistics;

    #My Modules----
    include("../MySQL/mysql_access.jl");
    include("./get_prices.jl");
    using .DBAccess, .prices;

    #Export functions----
    export riskFactors;



    #Functions----

    function riskFactors(test::Bool = false)
        #Busca de dados e pré-processamento para cálculo

        #Consultas
        tickers ::DataFrame = getTickers();
        prices  ::DataFrame = getPrices(test);
        stocks  ::DataFrame = getStocks();

        #Processamento dos preços
        returns ::DataFrame = calculateReturns(prices);

        calculatedFactors ::DataFrame = returns;
        calculateRiskFactors!(calculatedFactors, stocks);
#        CSV.write("../data/riskFactors.csv", calculatedFactors);
        return calculatedFactors;
    end



    function calculateRiskFactors!(factorsData::DataFrame, stocks::DataFrame)#::DataFrame
        #Cálculo dos fatores de risco
        sizeFactor!(factorsData, stocks);
        println(factorsData);
#        valueFactor!(factorsData, stocks);
#        liquidityFactor!(factorsData);
#        momentumFactor!(factorsData);
#        marketFactor!(factorsData);
#
#        return appendDataFrames(size, value, liquidity, momentum, market);
    end

    function sizeFactor!(factorsData::DataFrame, stocks::DataFrame) #::DataFrame
        marketCapitalization!(factorsData, stocks);
        createPortfolio!(factorsData, marketCap, med);

    end

    function marketCapitalization!(factorsData::DataFrame, stocks::DataFrame)
        for stock in unique(stocks."codigo_cvm")
            
            
        end
        
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


    #Util Functions----

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
