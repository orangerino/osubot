import time
import datetime
import tokens
import json


def time_converter(seconds):   # convert map length to common time format
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

def mods_converter(mods, convertion_mode=0):  # convert mods combination given by user to key format
    if not convertion_mode:
        if mods == "NOMOD":
            return 0
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
    if convertion_mode == 1:
        if mods == 0:
            return 'Nomod'
        combination = ''
        power = 0
        while mods > 0:
            while 2 ** power <= mods:
                power += 1
            else:
                power -= 1
                temp_key = 2 ** power
                combination = tokens.mods[str(temp_key)] + combination
                mods -= temp_key
                power = 0
        return combination


def write_map_to_db(beatmap_id, mods, pp):  # 3459267 HDDT 57.5
    with open("beatmap_db.json", 'r') as f:
        data = json.loads(f.read())
        data[mods][beatmap_id] = pp,
        data["everything"][beatmap_id] = (pp, mods)
    with open("beatmap_db.json", 'w') as f:
        f.write(json.dumps(data))

def write_rate_to_db(beatmap_id, rating, admin_mode=0):
    beatmap_id = str(beatmap_id)
    with open("rating_db.json", 'r') as f:
        data = json.loads(f.read())
        if beatmap_id not in data.keys():
            data[beatmap_id] = {"rating": 0, "count": 0}
        data[beatmap_id]["rating"] = round((data[beatmap_id]["count"] * data[beatmap_id]["rating"] + rating) / (data[beatmap_id]["count"] + 1), 2)
        if not admin_mode:
            data[beatmap_id]["count"] += 1
    with open("rating_db.json", 'w') as f:
        f.write(json.dumps(data))
