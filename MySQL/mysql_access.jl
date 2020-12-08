module DBAccess
    using DataFrames, MySQL;
    export getTickers, getStocks, getDF, getAccount;

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


    function executeQuery(query, env = "Prod")
        #Envia consulta ao BD
        connection = connectMySQL(env);
        result = DBInterface.execute(connection, query);
        result = DataFrame(result)
        DBInterface.close!(connection)
        return result
    end


    function getAccount(code ::String)
        #Busca uma conta específica de todas as empresas
        query = open(f->read(f, String), "../SQL/single_account_query.sql")
        query = replace(query, ":code:" => code)  
        return executeQuery(query) 
    end

    function getDF(cvm ::String)
        #Busca demonstrativos de uma determidada empresa
        query = open(f->read(f, String), "../SQL/getDF.sql")
        query = replace(query, ":cvm:" => cvm) 
        return executeQuery(query) 
    end

    function getTickers() ::DataFrame
        #Busca lista de tickers
        query = open(f->read(f, String), "../SQL/getTickers.sql")
        return executeQuery(query, "hml")
    end

    function getStocks() ::DataFrame
        #Busca quantidades de ações para cada empresa
        query = open(f->read(f, String), "../SQL/num_ações.sql")
        return executeQuery(query, "hml")        
    end
end


