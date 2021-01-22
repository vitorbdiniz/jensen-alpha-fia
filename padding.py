def verbose(msg, level, verbose=0):
    '''
        Printa mensagens na tela para um nível de verbose
        level in {1,2,3,4,5}
        verbose in {0,1,2,3,4,5}
    '''
    if level <= verbose:
        if msg[0] == '-' and msg[-1] == '-':
            msg = betwen_lines(msg)
        elif msg == "line" or msg == "l":
            msg = get_line()
        print(msg)
    
    return

def get_line():
    return "-------------------------------------------------------------------------------------------"

def betwen_lines(msg):
    s = 91 - len(msg)
    line = str("-" * int(s/2))
    return line + msg + line

def persist(data, path, persist=False):
    """
        Persiste DataFrames em um path

        - data: deve ser do tipo pd.DataFrame ou um iterável de pd.DataFrames

        - path: deve ser uma string ou uma lista de strings de mesmo tamanho de data
    """
    if persist:
        try:
            iter(data)
            if len(data) == len(path):
                for i in range(len(data)):
                    data[i].to_csv(path)
        except:
            data[i].to_csv(path)
    return 

