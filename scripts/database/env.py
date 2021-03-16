def define_matrix_env(env):
    if env == "prod" or env == "producao" or env == "produção":
        host = "10.55.192.42"
        user = "vitor.diniz"
        password = "-uV3Fg*yA^xh?2VR&tAu6LH"
        dbname = "tc_matrix"
    elif env == "hml" or env == "homolog" or env == "homologação":
        host = "10.249.240.10"
        user = "mmuser"
        password = "TradersPetr4"
        dbname = "tc_matrix"
    else:
        raise AttributeError("Definição incorreta do ambiente")
    return (host, user, password, dbname)


class env():
    def __init__(self, environement="prod"):
        self.host = self.__make_host(environement)
        self.user = self.__make_user(environement)
        self.password = self.__make_password(environement)
        self.dbname = self.__make_dbname(environement)

    def __make_host(self, environement):
        return "10.55.192.42" if environement == "prod" else "10.249.240.10"
    def __make_user(self,environement):
        return "vitor.diniz" if environement == "prod" else "mmuser"
    def __make_password(self,environement):
        return "-uV3Fg*yA^xh?2VR&tAu6LH" if environement == "prod" else "TradersPetr4"
    def __make_dbname(self,environement):
        return "tc_matrix"
    
    def defined_matrix_env(self):
        return (self.host, self.user, self.password, self.dbname)
    def get_host(self):
        return self.host
    def get_user(self):
        return self.user
    def get_password(self):
        return self.password
    def get_dbname(self):
        return self.dbname
