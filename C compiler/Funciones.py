def printf(string, var):
    if '%d' in string:
        string = string.replace('%d', str(var))
    elif '%f' in string:
        string = string.replace('%f', str(var))
    elif '%c' in string:
        string = string.replace('%c', str(var))
    print(string)

