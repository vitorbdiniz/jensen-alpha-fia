module DBAccess
    using DataFrames, MySQL;
    export getTickers, getDF, getAccount;

    function connectMySQL(environment = "prod")
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
        connection = connectMySQL(env);
        result = DBInterface.execute(connection, query);
        result = DataFrame(result)
        DBInterface.close!(connection)
        return result
    end


    function getAccount(code ::String)
        query = open(f->read(f, String), "../SQL/single_account_query.sql")
        query = replace(query, ":code:" => code)  
        return executeQuery(query) 
    end

    function getDF(cvm ::String)
        query = open(f->read(f, String), "../SQL/getDF.sql")
        query = replace(query, ":cvm:" => cvm) 
        return executeQuery(query) 
    end

    function getTickers() ::DataFrame
        query = open(f->read(f, String), "../SQL/getTickers.sql")
        return executeQuery(query, "hml")
    end    
end


