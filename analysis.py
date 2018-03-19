import sys
import glob
from collections import Counter
import requests
import pprint
from cfg import emotes_global, emotes_bttv_global, CLIENT_ID
from emotes import emotes_channels


def get_bttv_local(channel):
    emotes = requests.get("https://api.betterttv.net/2/channels/" + channel).json()
    if not 'emotes' in emotes:
        return [""]
    codes = [emote['code'] for emote in emotes['emotes']]
    return codes


def get_ffz_local(channel):
    emotes = requests.get("https://api.frankerfacez.com/v1/room/" + channel).json()
    if not 'sets' in emotes:
        return [""]
    
    
    emotes_data = emotes['sets'][str(list(emotes['sets'].keys())[0])]['emoticons']
    codes = [emote['name'] for emote in emotes_data]
    return codes


def print_files(files):
    for txt in files:
        print(txt.split("\\")[1])


def main():
    files = glob.glob("channels\\*.txt")    
    if len(sys.argv) == 1:
        print("Specify channel\n", "-"*10)
        print_files(files)
        return

    channel = sys.argv[1]
    if "channels\\{}.txt".format(channel) not in files:
        print("Wrong channel, available are: \n", "-"*10)
        print_files(files)
        return

    with open("channels\\{}.txt".format(channel), encoding="utf8") as f:
        data = f.readlines()

    emotes_all = emotes_global + emotes_bttv_global + get_bttv_local(channel) + get_ffz_local(channel)

    nicknames = []
    messages = []
    words = []
    emotes = []
    for msg in data:
        if msg == '\n':
            continue
        nicknames.append(msg.split(':')[0])
        messages.append(msg.split(':')[1].strip())

    for msg in messages:
        for spl in msg.split():
            words.append(spl)
            if spl in emotes_all:
                emotes.append(spl)

            for emote in emotes_channels:
                if emote in spl:
                    emotes.append(spl)

    while "@" + channel in emotes: 
        emotes.remove("@" + channel)

    
    if sys.argv[2] == "emote" or sys.argv[2] == "full":
        print("Top {} channel emotes\n".format(sys.argv[3]), "-"*20)
        c = Counter(emotes)
        pprint.pprint(c.most_common(int(sys.argv[3])))
        print("-"*20)

    if sys.argv[2] == "nick":
        print("Top {} most active chat members\n".format(sys.argv[3]), "-"*20)
        c = Counter(nicknames)
        pprint.pprint(c.most_common(int(sys.argv[3])))
        print("-"*20)

    if sys.argv[2] == "percent" or sys.argv[2] == "full":
        print("Emotes percent of all words\n", "-"*20)
        print((len(emotes)/len(words))*100)
        print("-"*20)

    if sys.argv[2] == "words":
        print("Top {} most used words\n".format(sys.argv[3]), "-"*20)
        c = Counter(words)
        pprint.pprint(c.most_common(int(sys.argv[3])))
        print("-"*20)

if __name__ == "__main__": 
    main()