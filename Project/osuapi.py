import requests
import json
import tokens
from misc import *

mods = tokens.mods
key = tokens.apikey
url = 'https://osu.ppy.sh/api/'
the_cooler_url = 'https://osu.gatari.pw/api/'


def getMapPP(beatmap_id, accuracy=[98, 99, 100], misses=0, maxcombo=0, mods=0):
    data = {}
    for acc in accuracy:
        try:
            if float(acc) > 100 or float(acc) < 0:
                return 'error'
        except ValueError:
            return 'error'
        data[str(acc)] = requests.get(the_cooler_url + 'v1/pp?b={}&a={}&x={}&c={}&m={}'.format(beatmap_id, acc, misses, maxcombo, mods)).json()
        data[str(acc)]['b_id'] = beatmap_id
        if mods != 0:
            data[str(acc)]['used_mods'] = tokens.mods[str(mods)]


    return data

def extractMapPP(beatmap_data):
    if beatmap_data == 'error':
        return 'Incorrect accuracy, must be between 0 and 100'
    bd_keys = list(beatmap_data.keys())
    default_beatmap_data = beatmap_data[bd_keys[0]]
    name = 'Beatmap: [{} {}]'.format('https://osu.ppy.sh/b/{}'.format(default_beatmap_data['b_id']), default_beatmap_data['song_name'])
    mods = ''
    if 'used_mods' in list(default_beatmap_data.keys()):
        mods = ' +{}'.format(default_beatmap_data['used_mods'])
    name = name + mods
    separator = ' | '
    acc_list = []
    for key in bd_keys:
        temp_acc = '{}%: {}pp'.format(key, beatmap_data[key]['pp'][0])
        acc_list.append(temp_acc)
    acc_amounts = separator.join(acc_list)
    length = 'Length: {}'.format(time_converter(int(default_beatmap_data['length'])))
    bpm = 'BPM: {}'.format(default_beatmap_data['bpm'])
    stars = 'SR: {}*'.format(round(float(default_beatmap_data['stars']), 2))
    ar = 'AR: {}'.format(default_beatmap_data['ar'])
    od = 'OD: {}'.format(default_beatmap_data['od'])
    ans = separator.join([name, acc_amounts, length, bpm, stars, ar, od])
    return ans


def getPlayerStats(player):
    try:
        data = requests.get(url + 'get_user?k={}&u={}'.format(key, player)).json()[0]
        return data
    except:
        return 'error'

def extractPlayerStats(data):
    if data == 'error' or not data:
        return 'error'
    keys = ['username', 'playcount', 'pp_raw', 'level', 'accuracy', 'country', 'join_date', 'total_seconds_played']
    if '%20' in data['username']:
        data['username'] = ' '.join(data['username'].split('%20'))
    if data['country'] in tokens.country_abb.keys():
        data['country'] = tokens.country_abb[data['country']]
    stats_data = []
    for key in keys:
        if key != 'pp_raw' and key != 'accuracy' and key != 'join_date' and key != 'total_seconds_played':
            temp_data = key[0].upper() + key[1:] + ": {}".format(data[key])
        elif key == 'accuracy':
            temp_data = 'Accuracy: {}%'.format(round(float(data[key]), 2))
        elif key == 'join_date':
            temp_data = 'Join date: {}'.format(refactorDate(data[key]))
        elif key == 'total_seconds_played':
            temp_data = 'Playtime: {} hours'.format(round(float(data[key])/3600, 2))
        else:
            temp_data = 'Performance Points: {}pp'.format(data[key])
        stats_data.append(temp_data)
    stats = ' | '.join(stats_data)
    return stats

def getBeatmapInfo(beatmap_id):
    beatmap_data = requests.get(url + 'get_beatmaps?k={}&b={}'.format(key, beatmap_id)).json()[0]
    return beatmap_data

def extractBeatmapInfo(beatmap_data):
    if beatmap_data != []:
        keys = ['artist', 'title']
        beatmap_info = []
    
        for key in keys:
            beatmap_info.append(beatmap_data[key])
        return beatmap_info
    else:
        return []

def getPlayerRecentScores(player):
    try:
        scores = requests.get(url + 'get_user_recent?k={}&u={}'.format(key, player)).json()
        return scores
    except:
        return 'error'

def extractPlayerRecentScores(scores):
    if scores == 'error':
        return scores
    if scores != []:
        enabled_mods = scores[0]['enabled_mods']
        beatmap_id = scores[0]['beatmap_id']
        beatmap_info = extractBeatmapInfo(getBeatmapInfo(beatmap_id))
        temp = ' - '.join(beatmap_info)
        if '&' in temp:
                index = temp.find('&')
                temp = temp[:index] + '-n-' + temp[index+1:]
        if enabled_mods != '0':
            return temp + ' with ' + mods[enabled_mods]
        else:
            return temp + ' Nomod '
    else:
        return ''

def getPlayerBest(player):
    return requests.get(url + 'get_user_best?k={}&u={}&limit=5'.format(tokens.apikey, player)).json()

def getPlayerAveragePP(data):
    total = 0
    for score in data:
        score_pp = float(score["pp"])
        total += score_pp
    return round(total / 5, 2)

def get_mapIdsfrommapset(mapset):
    ids = []
    data = requests.get(url + "get_beatmaps?k={}&s={}".format(tokens.apikey, mapset)).json()
    for map in data:
        ids.append(map["beatmap_id"])
    return ids


def learn(beatmaps):
    for beatmap_id in beatmaps:
        with open("beatmap_db.json", 'r') as f:
            data = json.loads(f.read())
            if str(beatmap_id) not in list(data["NOMOD"].keys()):
                mods_to_write = ['NOMOD', 'HD', 'DT', 'HR', 'HDDT', 'HDHR', 'HDHRDT']
                for mod in mods_to_write:
                    t_data = getMapPP(beatmap_id, [99], misses=0, maxcombo=0, mods=mods_converter(mod))
                    write_map_to_db(beatmap_id, mod, t_data['99']["pp"][0])
                    print('[{}] Learned beatmap {} with {} that gives total pp of {}'.format(format_time(time.time()), beatmap_id, mod, t_data['99']['pp'][0]))
        write_rate_to_db(beatmap_id, 0, 1)




