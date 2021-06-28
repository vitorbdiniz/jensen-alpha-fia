class database():
    def __init__(self, host, user, password, dbname):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname

    def defined_env(self):
        return (self.host, self.user, self.password, self.dbname)
    def get_host(self):
        return self.host
    def get_user(self):
        return self.user
    def get_password(self):
        return self.password
    def get_dbname(self):
        return self.dbname
    def __str__(self):
        return f'mysql://{self.host}:3306/{self.dbname}'



class risk_factors_db(database):
    def __init__(self):
        super(risk_factors_db, self).__init__('localhost', 'root', 'passwort', 'risk_factors')


class env(database):
    def __init__(self, environement="prod"):
        host = self.__make_host(environement)
        user = self.__make_user(environement)
        password = self.__make_password(environement)
        dbname = self.__make_dbname(environement)
        super(env, self).__init__(host, user, password, dbname)

    def __make_host(self, environement):
        return "10.55.192.42" if environement == "prod" else "10.249.240.10"
    def __make_user(self,environement):
        return "vitor.diniz" if environement == "prod" else "mmuser"
    def __make_password(self,environement):
        return "-uV3Fg*yA^xh?2VR&tAu6LH" if environement == "prod" else "TradersPetr4"
    def __make_dbname(self,environement):
        return "tc_matrix"
    
    def defined_matrix_env(self):
        return self.defined_env()

