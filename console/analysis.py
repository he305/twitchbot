import sys
import glob
from collections import Counter
import requests
import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from emotes import emotes_channels, emotes_bttv_global, emotes_global
import datetime
import math


class Message:
    def __init__(self, nickname, time, message):
        self.nickname = nickname
        self.time = time
        self.message = message

        self.split_message()
    
    def split_message(self):
        self.words = self.message.split()

        global emotes_all
        self.emotes = []
        for word in self.words:
            if word in emotes_all:
                self.emotes.append(word)
            for emote in emotes_channels:
                if emote in word:
                    self.emotes.append(word)
        
        self.words = [word.lower() for word in self.words if word not in self.emotes and len(word) >= 4]

        while "@" + channel in self.emotes: 
            self.emotes.remove("@" + channel)

        while "@" + channel in self.words:
            self.words.remove("@" + channel)


    def __lt__(self, other):
         return self.time < other.time


    def count_emote(self, emote):
        return self.emotes.count(emote)
            

emotes_all = []
channel = ""

def get_bttv_local(channel):
    files = glob.glob("emotes_channels\\*.txt")
    if "emotes_channels\\{}.txt".format(channel+'_bttv') in files:
        with open("emotes_channels\\{}.txt".format(channel+'_bttv'), encoding="utf8") as f:
            data = [d.strip() for d in f.readlines()]
        return data

    emotes = requests.get("https://api.betterttv.net/2/channels/" + channel).json()
    if not 'emotes' in emotes:
        return [""]
    codes = [emote['code'] for emote in emotes['emotes']]

    with open("emotes_channels\\{}.txt".format(channel+'_bttv'), 'w+', encoding="utf8") as f:
        for code in codes:
            f.write(code+'\n')

    return codes


def get_ffz_local(channel):
    files = glob.glob("emotes_channels\\*.txt")
    if "emotes_channels\\{}.txt".format(channel+'_ffz') in files:
        with open("emotes_channels\\{}.txt".format(channel+'_ffz'), encoding="utf8") as f:
            data = [d.strip() for d in f.readlines()]
        return data

    emotes = requests.get("https://api.frankerfacez.com/v1/room/" + channel).json()
    if not 'sets' in emotes or len(emotes['sets'][str(list(emotes['sets'].keys())[0])]['emoticons']) == 0:
        return [""]

    emotes_data = emotes['sets'][str(list(emotes['sets'].keys())[0])]['emoticons']
    codes = [emote['name'] for emote in emotes_data]

    with open("emotes_channels\\{}.txt".format(channel+'_ffz'), 'w+', encoding="utf8") as f:
        for code in codes:
            f.write(code+'\n')

    print(codes)
    return codes


def print_files(files):
    for txt in files:
        print(txt.split("\\")[1])


def get_dynamic(emote, messages):
    sorted_messages = sorted(messages, key=lambda message: message.time)
    emote_sum = 0
    x = []
    y = []
    start_time = messages[0].time
    prev_count = 0
    i = 0
    interval = math.floor(len(messages)/200)
    for msg in sorted_messages:
        emote_sum += msg.count_emote(emote)
        i += 1
        if i >= interval:
            if len(x) == 0:
                time = 0
            else:
                time = (msg.time - start_time)/datetime.timedelta(minutes=1)

            ###TEMPORARY###
            if len(x) > 1 and msg.time == x[-1]:
                continue
            ###############
            if sys.argv[4] == "delta":
                delta = emote_sum - prev_count
                prev_count = emote_sum
                y.append(delta)   
            elif sys.argv[4] == "graph":
                y.append(emote_sum)
            
            x.append(time)
            i = 0
    # data
    df=pd.DataFrame({'x': x, 'y': y})
    plt.title(emote)
    # plot
    plt.plot( 'x', 'y', data=df, linestyle='-')
    plt.show()



def main():
    files = glob.glob("channels\\*.txt")    
    if len(sys.argv) == 1:
        print("Specify channel\n", "-"*10)
        print_files(files)
        return

    global channel
    channel = sys.argv[1]
    if "channels\\{}.txt".format(channel) not in files:
        print("Wrong channel, available are: \n", "-"*10)
        print_files(files)
        return

    with open("channels\\{}.txt".format(channel), encoding="utf8") as f:
        data = f.readlines()


    global emotes_all
    emotes_all = emotes_global + emotes_bttv_global + get_bttv_local(channel) + get_ffz_local(channel)    

    messages = []
    words = []
    emotes = []
    nicknames = []

    with open('bots.txt', 'r', encoding="utf8") as f:
        bots = [b.strip() for b in f.readlines()]

    for msg in data:
        if msg == '\n':
            continue

        ###TEMPORARY
        data_msg = msg.split(':')
        if len(data_msg) == 2 or len(data_msg[0]) != 19:
            nickname = data_msg[0]
            message = data_msg[1].strip()
            time = datetime.datetime.strptime("2018-03-19 20-00-00", "%Y-%m-%d %H-%M-%S")
        else:
            nickname = data_msg[1]

            #Ignore bots, see bots.txt file
            if nickname in bots:
                continue

            time = datetime.datetime.strptime(data_msg[0], "%Y-%m-%d %H-%M-%S")
            message = data_msg[2].strip()
        
        messages.append(Message(nickname, time, message))


    for msg in messages:
        words += msg.words
        emotes += msg.emotes
        nicknames.append(msg.nickname)


    
    if sys.argv[2] == "emotes" or sys.argv[2] == "full":
        if len(sys.argv) == 3:
            top = 20
        else:
            top = sys.argv[3]

        print("Top {} channel emotes\n".format(top), "-"*20)
        c = Counter(emotes)
        pprint.pprint(c.most_common(int(top)))
        print("-"*20)

    if sys.argv[2] == "nick":
        print("Top {} most active chat members\n".format(sys.argv[3]), "-"*20)
        c = Counter(nicknames)
        pprint.pprint(c.most_common(int(sys.argv[3])))
        print("-"*20)

    if sys.argv[2] == "percent" or sys.argv[2] == "full":
        print("Emotes percent of all words\n", "-"*20)
        print((len(emotes)/(len(words)+len(emotes)))*100)
        print("-"*20)

    if sys.argv[2] == "words":
        if len(sys.argv) == 3:
            top = 20
        else:
            top = sys.argv[3]

        print("Top {} most used words\n{}".format(top, "-"*20))
        c = Counter(words)
        pprint.pprint(c.most_common(int(top)))
        print("-"*20)
    
    if sys.argv[2] == "emote":
        get_dynamic(sys.argv[3], messages)

if __name__ == "__main__": 
    main()