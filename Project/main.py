import socket
import osuapi
import time
import tokens
import help_lines
from misc import *
from random import *

threshold = 3*60 + 5  # ping-pong threshold.
last_ping = time.time() # if difference between ping times is bigger than bot will reconnect to server

last_asked_beatmap = {  # this dict contains last requested beatmap by each user so we can
    "Oranger": {  # return info for !acc or !mods commands without asking id from user again
        "beatmap_id": 520914,
        "mods": 0
    }
}


def sendPp(beatmap, mods=0, accuracy=[95, 99, 100],  sender=None):  # use api methods to receive info about beatmap
    last_asked_beatmap[sender] = {}  # the main thing to know is PP you will get by FCing with specific accuracy
    last_asked_beatmap[sender]["beatmap_id"] = beatmap
    last_asked_beatmap[sender]["mods"] = mods
    bot.send_private_message(sender, osuapi.extractMapPP(osuapi.getMapPP(beatmap, accuracy=accuracy, mods=mods)))
    osuapi.learn([beatmap])


def sendPpForSpecificMods():  # use api methods to receive info about beatmap but in difference with function before
    pass  # this can give you PP you'll get by FCing with specific mods


def sendPlayerStats(player, sender):  # use api methods to receive user information
    if '%20' in player:
        player = ' '.join(player.split('%20'))
    words = 'Player stats for {}: '.format(player)
    message = osuapi.extractPlayerStats(osuapi.getPlayerStats(player))
    if message == 'error':
        bot.send_private_message(sender, "This player doesn't seem to exist! Try again")
    else:
        bot.send_private_message(sender, words + message)

def recommendMap(player, mods=0, sender="None"):
    average_pp = osuapi.getPlayerAveragePP(osuapi.getPlayerBest(player))
    if mods == 0:
        amods = "NOMOD"
    else:
        mods = mods_converter(mods.upper())
        if mods != "error":
            amods = mods_converter(mods, 1)
        else:
            bot.send_private_message(sender, "I don't know such mods! Try again!")
            return
    maps = []
    rates = []
    try:
        with open("beatmap_db.json", 'r') as f:
            data = json.loads(f.read())
            for map in sample(list(data[amods].keys()), len(list(data[amods].keys()))):
                pp = data[amods][map][0]
                if average_pp - 0.15*average_pp < pp < average_pp + 0.15*average_pp:
                    maps.append(map)
                    if len(maps) == 3:
                        break
    except:
        bot.send_private_message(sender, "I don't support this mod for recommendations. The only suppoted !rec mods are HD, DT, HR")
        return


    with open("rating_db.json", 'r') as f:
        data = json.loads(f.read())
        for map in maps:
            rates.append(data[map]["rating"])

    s = round(sum(rates) * 10)
    key = randint(0, s)
    if 0 <= key <= round(max(rates) * 10):
        sendPp(maps[rates.index(max(rates))], mods=mods, sender=sender)
        last_asked_beatmap[sender]["beatmap_id"] = maps[rates.index(max(rates))]
        last_asked_beatmap[sender]["mods"] = mods
    elif round(max(rates) * 10) + 1 <= key <= round(max(rates) * 10) + round(min(rates) * 10):
        sendPp(maps[rates.index(min(rates))], mods=mods, sender=sender)
        last_asked_beatmap[sender]["beatmap_id"] = maps[rates.index(min(rates))]
        last_asked_beatmap[sender]["mods"] = mods
    else:
        maps.remove(max(maps))
        sendPp(maps[rates.index(max(rates))], mods=mods, sender=sender)
        last_asked_beatmap[sender]["beatmap_id"] = maps[rates.index(max(rates))]
        last_asked_beatmap[sender]["mods"] = mods




def rateMap(beatmap_id, rating, sender):
    rating_comp = {
        "unplayable": 1,
        "bad": 2,
        "good": 3
    }
    if rating in rating_comp.keys():
        rating_num = rating_comp[rating]
    else:
        bot.send_private_message(sender, '{} is not an rating option, try again'.format(rating[0].upper() + rating[1:].lower()))
        return
    write_rate_to_db(beatmap_id, rating_num)
    bot.send_private_message(sender, 'Map was rated as {}, thanks for your feedback'.format(rating))

def getLastPlayedMaps(player, sender):
    words = 'Last played maps for {}: '.format(player)
    words1 = 'No map was played recently.'
    message = osuapi.extractPlayerRecentScores(osuapi.getPlayerRecentScores(player))
    if message == 'error':
        bot.send_private_message(sender, 'Error! Try again')
    elif message == '':
        bot.send_private_message(sender, words1)
    else:
        bot.send_private_message(sender, words+message)


def getSupporterTime():
    pass


def skip(self, *args):
    pass

def help(sender):
    greetings = "Hello, I'm Oranger osu! bot. Here is my command list: "
    bot.send_private_message(sender, greetings)
    for i in range(7):
        bot.send_private_message(sender, help_lines.lines[str(i+1)])


class OrangerinoOsuBot:
    def __init__(self):
        self.settings = {
            "host": "irc.ppy.sh",
            "port": 6667,
            "channel": "#osu",
            "contact": "!",
            "botnick": tokens.nickname,
            "adminname": tokens.nickname,
            "password": tokens.password
            }

        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.actions = []

    def server_connect(self):  # connection to Bancho IRC server
        print("[{}] Connecting to {}:{}...".format(format_time(time.time()), self.settings["host"], self.settings["port"]))
        self.ircsock.connect((self.settings["host"], self.settings["port"]))
        print("[{}] Logging in...".format(format_time(time.time())))
        self.ircsock.send(("PASS {}\n".format(self.settings["password"])).encode())
        self.ircsock.send(("NICK {}\n".format(self.settings["botnick"])).encode())
        self.ircsock.send(
            ("USER {} {} name: {}\n".format(self.settings["botnick"], self.settings["botnick"], self.settings["botnick"])).encode())
        print("[{}] Successfully logged in".format(format_time(time.time())))

    def join_channel(self):  # joining main #osu channel
        print("[{}] joining channel {}...".format(format_time(time.time()), self.settings["channel"]))
        self.ircsock.send(("JOIN {}\n".format(self.settings["channel"])).encode())
        print("[{}] successfully joined the channel {}.".format(format_time(time.time()), self.settings["channel"]))

    def leave_channel(self):  # leaving channel
        print("[{}] leaving the channel {}...".format(format_time(time.time()), self.settings["channel"]))
        self.ircsock.send(("PART {}\n".format(self.settings["channel"])).encode())
        print("[{}] successfully left the channel {}.".format(format_time(time.time()), self.settings["channel"]))

    def restart(self):  # reconnecting to server in case we get disconnected by it
        print("[{}] leaving {}:{}".format(format_time(time.time()), self.settings["host"], self.settings["port"]))
        print("[{}] closing socket".format(format_time(time.time())))
        self.ircsock.close()
        print("[{}] creating new socket".format(format_time(time.time())))
        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connect()

    def send_private_message(self, user=None, message=None, operation=None):  # sending message/operation like PONG
        if not message:
            self.ircsock.send(("{} {}\n".format(operation, self.settings["channel"])).encode())
        print("[{}] sending message '{}' to {}".format(format_time(time.time()), message, user))
        self.ircsock.send(("PRIVMSG {} :{}\n".format(user, message)).encode())

    def parse_input(self):  # parsing data we getting from IRC server
        try:
            data = self.ircsock.recv(2048)
            data = data.decode('utf-8')
            data = data.split('\n')
            for action in data:
                    command = action.split()[1]
                    sender = action.split()[0]
                    sender = sender.strip('!cho@ppy.sh')
                    sender = sender[1:]
                    if command == 'PRIVMSG':
                        if action.split()[2] == self.settings["botnick"]:
                            received_message = (' '.join(action.split()[3:]))[1:]
                            self.actions.append([sender, received_message])
                            print(sender, received_message)# we collect actions in bot's body so we can do them by one by one and don't forget about any of them
                    if command.find('PING') != -1:
                        last_ping = time.time()
                        self.send_private_message(message="PONG "+command.split()[1]+"\r\n")
        except Exception:
            pass

    def handle_actions(self):  # responding to actions
        for action in self.actions:
            call = action[1].split()[0]
            args = action[1].split()[1:]
            sender = action[0]
            if 'ACTION is playing' in action[1] or 'ACTION is listening' in action[1]:  # checking if private message is /np command
                if 'playing' in action[1]:
                    beatmap_id = action[1].split()[3].strip('[https://osu.ppy.sh/b/')
                else:
                    beatmap_id = action[1].split()[4].strip('[https://osu.ppy.sh/b/')  # length of given message depends on whether it's playing or listening to
                mods = ''
                for word in action[1].split():
                    if '+' in word and word[1:] in tokens.mods_from_words_to_abb.keys():
                        mods += tokens.mods_from_words_to_abb[word[1:]]
                    elif word[1:-1] in tokens.mods_from_words_to_abb.keys():
                        mods += tokens.mods_from_words_to_abb[word[1:-1]]
                mods = mods_converter(mods)
                command = sendPp
                args = [beatmap_id, mods, [98, 99, 100]]  # /np calls function that will return beatmap info and pp for stock accuracies (98, 99, 100)
            elif call == '!acc':
                command = sendPp
                args = [last_asked_beatmap[sender]["beatmap_id"], last_asked_beatmap[sender]["mods"], [args[0]]]
            elif call == '!mods':
                command = sendPp
                mods = mods_converter(args[0].upper())
                args = [last_asked_beatmap[sender]["beatmap_id"], mods, [98, 99, 100]]
            elif call == '!last':
                command = getLastPlayedMaps
            elif call == '!stats':
                command = sendPlayerStats
                if len(args) > 1:
                    args = ["%20".join(args)]
            elif call == '!rec':
                command = recommendMap
                if args:
                    args = [sender, args[0]]
                else:
                    args = [sender, 0]
            elif call == '!rate':
                command = rateMap
                args = [last_asked_beatmap[sender]["beatmap_id"]]+ [' '.join(action[1].split()[1:])]
            elif call == '!help':
                command = help
                args = []
            else:
                command = skip
            args = args + [sender]
            command(*args)
        self.actions = []  # cleaning actions queue as we respond to each one


bot = OrangerinoOsuBot()
bot.server_connect()

def main():
    global last_ping
    bot.join_channel()
    while True:
        bot.parse_input()
        bot.handle_actions()
        if (time.time() - last_ping) > threshold:  # restarting in case of disconnection
            last_ping = time.time()
            bot.leave_channel()
            bot.restart()
            break

while True:
    main()
