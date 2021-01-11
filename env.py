def define_matrix_env(env):
    if env == "prod" or env == "producao" or env == "produção":
        host = "10.55.192.17"
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
