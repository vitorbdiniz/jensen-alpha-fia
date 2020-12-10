module criteria
    using DataFrames, Dates;

    include("../utils.jl");
    using .utils;



    export elegibilityCriteria!;

    function elegibilityCriteria!(prices::DataFrame, verbose::Bool)
        # Selecionar ações com alguma liquidez em, pelo menos, 80% (200 dias) dos pregões para o último ano
        verboseMessage(verbose, "- Avaliando liquidez anual");
        liquidityCriterion!(prices, verbose);

        # Selecionar ação mais negociada da empresa
        verboseMessage(verbose, "- Avaliando liquidez por ticker da empresa");
        stockCriterion!(prices);

        # listada desde dez/(t-1)
        verboseMessage(verbose, "- Avaliando tempo de listagem");
        timeCriterion!(prices);
        
    end 

    function liquidityCriterion!(prices::DataFrame, verbose::Bool)
        len:: Int64 = nrow(prices);
        initial_index::Int64 = 1;
        i::Int64 = 1;
        minimumDesirable::Int64 = 200;
        counter::Int64 = 0;

        ticker_id::Int64 = prices."ticker_id"[1];
        initial_date::Date = prices."date"[1];

        while i <= len
            if ticker_id == prices."ticker_id"[i]
                if Dates.year(initial_date) != Dates.year(prices."date"[i])
                    if counter < 200
                        deleteDataFrameRows!(prices, initial_index, i-1);
                        i = initial_index;
                        len = nrow(prices);
                    else
                        initial_index = i;
                    end
                    initial_date = prices."date"[i];
                    counter = 0;
                    ticker_id = prices."ticker_id"[i];
                end
            else
                if counter < 200
                    deleteDataFrameRows!(prices, initial_index, i-1);
                    i = initial_index;
                    len = nrow(prices);
                else
                    initial_index = i;
                end
                initial_date = prices."date"[i];
                counter = 0;
                ticker_id = prices."ticker_id"[i];
                verboseMessage(verbose, string(i)*". "*string(prices."ticker_id"[i]));

            end

            if prices."Volume"[i] > 0
                counter += 1; 
            end
            i += 1;

        end
    end
    function stockCriterion!(prices::DataFrame)
        println("TODO")
    end
    function timeCriterion!(prices::DataFrame)
        println("TODO")
    end


    
end