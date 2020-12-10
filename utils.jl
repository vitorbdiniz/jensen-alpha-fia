module utils

    using DataFrames, Dates, CSV;

    export killUnits!, getStockDate, getStockNumber, persistDataFrame, verboseMessage, deleteDataFrameRows!;


    function killUnits!(tickers::DataFrame)
        len::Int64 = nrow(tickers);
        i::Int64 = 1;
        while i <= len
            if tickers."codigo_negociacao"[i][lastindex(tickers."codigo_negociacao"[i])] == '1'
                delete!(tickers, i);
                len -= 1;
            end
            i += 1;
        end
        
    end

    function getStockNumber(stocks::DataFrame, codigo_cvm::Int64, date::Date) ::Array{Int64, 1}
        stockNumber::Array{Int64, 1} = [];
        refDate::Date = getStockDate(stocks, date, codigo_cvm);
        for i in 1:nrow(stocks)
            if stocks."data_referencia"[i] == refDate && stocks."codigo_cvm"[i] == codigo_cvm
                append!(stockNumber, stocks."ordinarias"[i]);
                append!(stockNumber, stocks."preferenciais"[i]);
                append!(stockNumber, stocks."totais"[i]);
                break;
            end
        end 
        return stockNumber;
    end
    function getStockDate(stocks::DataFrame, date::Date, codigo_cvm::Int64) ::Date
        selectedDate ::Date = Date(2000, 1, 1);
        for i in 1:nrow(stocks)
            if stocks."codigo_cvm"[i] == codigo_cvm
                if stocks."data_referencia"[i] < date
                    selectedDate = stocks."data_referencia"[i];
                elseif selectedDate == Date(2000, 1, 1)
                    selectedDate = stocks."data_referencia"[i];
                    break;
                else
                    break;
                end    
            end
        end
        return selectedDate;
    end



    function verboseMessage(verbose::Bool, msg::String)
        if verbose
            println(msg);
        end
    end

    function persistDataFrame(df::DataFrame, path::String, persist::Bool)
        if persist
            CSV.write(path, df);            
        end
    end

    function deleteDataFrameRows!(prices::DataFrame, initial_index::Int64, final_index::Int64)
        for i in initial_index:final_index
            delete!(prices, initial_index);
        end
        
    end


end