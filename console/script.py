import requests
import pprint
import json
from cfg import CLIENT_ID
from time import sleep
import os
import subprocess

def main():
    with open('streamers.txt', mode='r', encoding='utf8') as f:
        streamers = [s.strip() for s in f.readlines()]

    print("Overwatched streamers:")
    for streamer in streamers:
        print(streamer)

    headers = {
        'Client-ID' : CLIENT_ID,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }


    while True:
        for streamer in streamers:
            stream_data = requests.get("https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('saving', ''), headers=headers).json()
            
            if 'error' in stream_data:
                sleep(20)
                continue

            if not stream_data['data'] and 'saving' in streamer:
                streamers[streamers.index(streamer)] = streamer.replace('saving', '')
            if stream_data['data'] and not 'saving' in streamer:
                print("{} stream is starting".format(streamer))
                subprocess.Popen("python bot.py " + streamer, creationflags=subprocess.CREATE_NEW_CONSOLE)
                streamers[streamers.index(streamer)] = 'saving' + streamer
        sleep(120)

if __name__ == "__main__":
    main()