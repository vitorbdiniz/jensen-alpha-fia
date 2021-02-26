def verbose(msg, level, verbose=0):
    '''
        Printa mensagens na tela para um nível de verbose
        level in {1,2,3,4,5}
        v in {0,1,2,3,4,5}
    '''
    if level <= verbose:
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

