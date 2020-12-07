

module pandas_datareader
    using PyCall, DataFrames, Dates;    
    export getPrices;

    function getPrices(tickers) ::DataFrames.DataFrame
        web = pyimport("pandas_datareader");
        result = DataFrames.DataFrame();
        errors::Array = [];
        
        for i in 1:length(tickers."codigo_negociacao")
            ticker  = eraseCharacters(tickers."codigo_negociacao"[i], 1) * ".SA";
            
                println(string(i)*". Buscando dados de "*string(ticker));

                a = web.get_data_yahoo(ticker, "2010-12-31", Dates.today())
                 
                println(a)
                #prices::DataFrame = ;
                #println(prices)
                #append!(result, prices);
            
                println("--- Erro com dados de " *ticker)
                #append!(errors, ticker);
            


        end
        return result;
    end

    function eraseCharacters(str::String, i::Int) ::String
        result::String = "";
        for i in i+1:length(str)
            result = result*str[i]
        end
        return result;
    end

end