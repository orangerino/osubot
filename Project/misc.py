import time
import datetime
import tokens

def time_converter(seconds): # convert map length to common time format
    hhmmss = [0, 0, 0]
    separator = ':'
    zero = '00'
    seconds = int(seconds)
    hhmmss[0] = seconds // 3600
    seconds %= 3600
    hhmmss[1] = seconds // 60
    seconds %= 60
    hhmmss[2] = seconds
    for i in range(len(hhmmss)):
        if hhmmss[i] > 9:
            hhmmss[i] = str(hhmmss[i])
        else:
            hhmmss[i] = '0'+str(hhmmss[i])
    if hhmmss[0] == zero:
        del hhmmss[0]
        if hhmmss[0][0] == zero[0]:
            hhmmss[0] = hhmmss[0][1:]
    time_str = separator.join(hhmmss)    # formatted as followed: hh:mm:ss
    return time_str


def refactorDate(date):
    d = date.split()[0]
    t = date.split()[1]
    year, month, day = d.split('-')
    hour, minute, second = t.split(':')
    return "{}-{}-{} {}.{}.{}".format(hour, minute, second, day, month, year)


def format_time(secs):
    t = time.ctime(time.time()).split()
    months = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jal": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    return "{} {}.{}.{}".format(t[3], t[2], months[t[1]], t[-1])

def mods_converter(mods):  # convert mods combination given by user to key format
    check = len(mods) % 2
    if check != 0:
        return 'error'
    len_by2 = len(mods) // 2
    final_key = 0
    for i in range(len_by2):
        temp_mod = mods[i*2:(i+1)*2]
        if temp_mod in tokens.mods.values():
            for mod_keys in tokens.mods.keys():
                if temp_mod == tokens.mods[mod_keys]:
                    final_key += int(mod_keys)
        else:
            return 'error'
    return final_key
