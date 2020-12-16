module factors

    #Libs----
    using DataFrames, CSV, Dates, Statistics;

    #Include Modules----
    include("../MySQL/mysql_access.jl");
    include("../utils.jl");
    using .criteria, .utils;

    #Export functions----
    export riskFactors;



    #Functions----

    function riskFactors(;verbose::Bool = false)
        #Busca de dados e pré-processamento para cálculo

        verboseMessage(verbose, "Verificando elegibilidade");
        elegibilityCriteria!(prices, tickers, verbose);
#        persistDataFrame(prices, "./data/prices.csv", persist);

        # Processamento dos retornos
        
        


        # Cálculo de fatores de risco
        calculatedFactors ::DataFrame = returns;
        verboseMessage(verbose, "Calculando fatores de risco");
        calculateRiskFactors!(calculatedFactors, stocks, verbose);
        persistDataFrame(calculatedFactors, "./data/riskFactors.csv", persist);

        return calculatedFactors;
    end


    function calculateRiskFactors!(factorsData::DataFrame, stocks::DataFrame, verbose::Bool)#::DataFrame
        #Cálculo dos fatores de risco

        verboseMessage(verbose, "- Calculando fator tamanho");
        sizeFactor!(factorsData, stocks, verbose);
        #println(factorsData);

        verboseMessage(verbose, "- Calculando fator valor");
        #valueFactor!(factorsData, stocks);

        verboseMessage(verbose, "- Calculando fator liquidez");
        #liquidityFactor!(factorsData);

        verboseMessage(verbose, "- Calculando fator momento");
        #momentumFactor!(factorsData);

        verboseMessage(verbose, "- Calculando fator mercado");
        #marketFactor!(factorsData);

        verboseMessage(verbose, "- Calculando fator beta");
        #betaFactor!(factorsData);
        verboseMessage(verbose, "- Calculando fator qualidade");
        #qualityFactor!(factorsData);

#        return appendDataFrames(size, value, liquidity, momentum, market);
    end

    function sizeFactor!(factorsData::DataFrame, stocks::DataFrame, verbose::Bool) #::DataFrame
        verboseMessage(verbose, "-- Calculando valores de mercado")

        marketCapitalization!(factorsData, stocks, verbose);
        createPortfolio!(factorsData);
    end
    function createPortfolio!(factorsData::DataFrame)

        
    end


    function marketCapitalization!(factorsData::DataFrame, stocks::DataFrame, verbose::Bool)
        marketCap::Array{Float64, 1} = [];
        len::Int64 = nrow(factorsData);
        i::Int64 = 1;
        while i <= len
            #nStocks[1] == ordinárias; nStocks[2] == preferenciais; nStocks[3] == totais
            nStocks::Array{Int64,1} = getStockNumber(stocks, factorsData."codigo_cvm"[i], factorsData."data"[i]);
            
            try
                if factorsData."codigo_negociacao"[i][lastindex(factorsData."codigo_negociacao"[i])] == '3'
                    append!(marketCap, nStocks[1]*factorsData."price"[i]);
                else
                    append!(marketCap, nStocks[2]*factorsData."price"[i]);
                end                
                i+=1;
            catch
                if verbose
                    println(factorsData."codigo_negociacao"[i] *" apresentou erro em "* Dates.format(factorsData."data"[i], "yyyy-mm-dd"));
                end
                delete!(factorsData, i);
                len-=1;
            end
        end
        insertcols!(factorsData, ncol(factorsData)+1, :valorMercado => marketCap);
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

#Portfolio Functions----




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

    function calculateReturns(prices::DataFrame, verbose::Bool = false)
        #Calcula retornos diários

        verboseMessage(verbose, "Calculando retornos");

        ret::Array{Float64, 1} = [];
        for i in 2:nrow(prices)
            append!(ret, prices."Adj Close"[i]/prices."Adj Close"[i-1]-1);
        end
        delete!(prices, 1);

        returns::DataFrame = DataFrame(codigo_cvm = prices."codigo_cvm", ticker_id = prices."ticker_id",codigo_negociacao = prices."codigo_negociacao",data=prices."date",price = prices."Adj Close",retornos = ret, volume = prices."Volume");
        persistDataFrame(returns, "./data/returns.csv", persist);

        return returns
    end


end