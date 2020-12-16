module DBAccess
    using DataFrames, MySQL;
    include("../utils.jl");
    using .utils;

    export getTickers, getStocks, getDF, getAccount, getStockQuantity;

    function connectMySQL(environment = "prod")
        #Conexão com o BD
        if environment == "prod"
            host = "10.55.192.17";
            user = "vitor.diniz";
            password = "-uV3Fg*yA^xh?2VR&tAu6LH";
            dbname = "tc_matrix";
        elseif environment == "hml"
            host = "10.249.240.10";
            user = "mmuser";
            password = "TradersPetr4";
            dbname = "tc_matrix";
        else
            println("Ambiente não definido")
        end

        return DBInterface.connect(MySQL.Connection, host, user, password, db=dbname);
    end


    function executeQuery(query, env = "Prod") ::DataFrame
        #Envia consulta ao BD
        connection = connectMySQL(env);
        result = DBInterface.execute(connection, query);
        result = DataFrame(result)
        DBInterface.close!(connection)
        return result
    end


    function getAccount(code ::String) ::DataFrame
        #Busca uma conta específica de todas as empresas
        query = open(f->read(f, String), "./MySQL/SQL/single_account_query.sql")
        query = replace(query, ":code:" => code)  
        return executeQuery(query) 
    end

    function getDF(cvm ::String) ::DataFrame
        #Busca demonstrativos de uma determidada empresa
        query = open(f->read(f, String), "./MySQL/SQL/getDF.sql")
        query = replace(query, ":cvm:" => cvm) 
        return executeQuery(query) 
    end

    function getTickers(verbose::Bool=false, persist::Bool=false) ::DataFrame
        #Busca lista de tickers
        verboseMessage(verbose, "Buscando tickers");
        
        query = open(f->read(f, String), "./MySQL/SQL/getTickers.sql")
        result::DataFrame = executeQuery(query, "hml");
        
        persistDataFrame(result, "./data/tickers.csv", persist);        
        return result;
    end

    function getStocks(verbose::Bool=false, persist::Bool=false) ::DataFrame
        #Busca quantidades de ações para cada empresa
        verboseMessage(verbose, "Buscando ações");
        
        query = open(f->read(f, String), "./MySQL/SQL/stocks.sql")
        result::DataFrame = executeQuery(query, "hml");

        persistDataFrame(result, "./data/stocks.csv", persist);
        return result;
    end
    function getStockQuantity(verbose::Bool=false, persist::Bool=false)::DataFrame
        
        query = open(f->read(f, String), "./MySQL/SQL/numberTickers.sql")
        return executeQuery(query, "hml")        
    end
end


