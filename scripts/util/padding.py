import pandas as pd
#Verbose configurations

def verbose(msg, level, verbose=0):
    '''
        Printa mensagens na tela para um nível de verbose
        level in {1,2,3,4,5}
        v in {0,1,2,3,4,5}
    '''
    if msg != '' and level <= verbose:
        if msg[0] == '-' and msg[-1] == '-':
            msg = betwen_lines(msg)
        elif msg == "line" or msg == "l":
            msg = get_line()
        print(msg)
    
    return

def get_line():
    return "-"*91

def betwen_lines(msg):
    s = 91 - len(msg)
    line = str("-" * int(s/2))
    return line + msg + line

#Persist configurations

def persist(df, path, to_persist=False, _verbose=0, verbose_level=0, verbose_str=""):
    if to_persist:
        verbose(verbose_str, level=verbose_level, verbose=_verbose)
        df.to_csv(path)
        verbose("-- OK.", level=verbose_level, verbose=_verbose)
        
def persist_collection(collection, path, extension=".csv", to_persist=False, _verbose=0, verbose_level=0, verbose_str=""):
    if to_persist:
        verbose(verbose_str, level=verbose_level, verbose=_verbose)
        for c in collection:
            c_path = path + str(c) + extension
            persist(collection[c], c_path, to_persist=to_persist)
        verbose("-- OK.", level=verbose_level, verbose=_verbose)
