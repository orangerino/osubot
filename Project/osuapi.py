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
    if mods != 0:
        mods = mods_converter(mods)
    for acc in accuracy:
        data[str(acc)] = requests.get(the_cooler_url + 'v1/pp?b={}&a={}&x={}&c={}&m={}'.format(beatmap_id, acc, misses, maxcombo, mods)).json()
        if mods != 0:
            data[str(acc)]['used_mods'] = tokens.mods[str(mods)]
    return data

def extractMapPP(beatmap_data):
    bd_keys = list(beatmap_data.keys())
    default_beatmap_data = beatmap_data[bd_keys[0]]
    name = 'Beatmap: {}'.format(default_beatmap_data['song_name'])
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

def extractMapPP_mods(beatmap_data):
    default_beatmap_data = extractMapPP(beatmap_data)

def getPlayerStats(player):
    try:
        data = requests.get(url + 'get_user?k={}&u={}'.format(key, player)).json()[0]
        return data
    except:
        return 'error'

def extractPlayerStats(data):
    if data == 'error' or not data:
        return data
    keys = ['username', 'playcount', 'pp_raw', 'level', 'accuracy', 'country']
    stats_data = []
    for key in keys:
        if key != 'pp_raw' and key != 'accuracy':
            temp_data = key[0].upper() + key[1:] + ": {}".format(data[key])
        elif key == 'accuracy':
            temp_data = 'Accuracy: {}'.format(round(float(data[key]), 2))
        else:
            temp_data = 'Performance Points: {}'.format(data[key])
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


