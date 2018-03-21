import sys
import cfg
import utils
import socket
import re
import threading
from time import sleep
import datetime
import requests
from cfg import CLIENT_ID
import shutil
import os

messages = []
running = False

def main():
    if len(sys.argv) == 1:
        print("Input channel name")
        return 

    cfg.CHANNEL = sys.argv[1]

    headers = {
        'Client-ID' : CLIENT_ID,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }
    
    stream_data = requests.get("https://api.twitch.tv/helix/streams?user_login=" + cfg.CHANNEL, headers=headers).json()
    
    global ignore_offline
    if len(sys.argv) == 3 and sys.argv[2] == "ignore":
        ignore_offline = True
    else:
        ignore_offline = False

    if not stream_data['data']:
        print("Stream is offline, continue anyway Y/N")
        if input() == "N":
            return
        ignore_offline = True
    
    paste_stream_start(stream_data['data'])

    global running
    running = True
    chat_thread.start()
    save_thread.start()


    while True:
        if running == False:
            print("Stopping the bot")
            if (check_online_thread.is_alive()):
                check_online_thread.join()
            chat_thread.join()
            print("Chat thread is stopped")
            save_thread.join()
            print("Saving thread is stopped")
            save()
            print("Quiting...")
            sys.exit()
        sleep(1)


def paste_stream_start(stream_data):
    
    d = datetime.datetime.strptime(stream_data[0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')
    d = d.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    time = d.strftime("%Y-%m-%d %H-%M-%S")

    message = "{0}:{1}: {2}\n".format(time, "he305bot", "Stream started")
    
    try:
        with open("channels/" + cfg.CHANNEL +'.txt', 'r+', encoding='utf8') as fp:
            lines = fp.readlines()
            if message.strip() != lines[0].strip():
                if os.path.isfile("channels/" + cfg.CHANNEL +'_old.txt'): 
                    shutil.copy2("channels/" + cfg.CHANNEL +'_old.txt', "channels/" + cfg.CHANNEL + "_old_old.txt")
                shutil.copy2("channels/" + cfg.CHANNEL +'.txt', "channels/" + cfg.CHANNEL + "_old.txt")
                fp.seek(0)
                fp.truncate()
                fp.write(message)
                
    except IOError:
        with open("channels/" + cfg.CHANNEL +'.txt', 'w', encoding='utf8') as fp:
            fp.write(message)


def check_online():
    headers = {
        'Client-ID' : CLIENT_ID,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }

    global running
    global s
    while running:
        stream_data = requests.get("https://api.twitch.tv/helix/streams?user_login=" + cfg.CHANNEL, headers=headers).json()
        if not stream_data['data']:
            print("Streamer has gone offline, finishing...")
            running = False
            utils.msg(s, "4Head")
            return
        print("-"*10)
        print(cfg.CHANNEL + " STREAM IS LIVE")
        print("-"*10)
        sleep(60)
        

def read_chat():
    global s
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(cfg.CHANNEL).encode("utf-8"))
    s.settimeout(120)
    global running

    chat_message = re.compile(r":?\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

    global ignore_offline
    if not ignore_offline:
        check_online_thread.start()
    while running:
        try:
            response = s.recv(1024).decode("utf-8")
            if response == "PING :tmi.twitch.tv\r\n":
                s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            else:
                data = response.splitlines()
                for res in data:
                    message = chat_message.sub("", res).strip()
                    if re.search(r"\w+", res) is not None:
                        full_message = "{0}: {1}".format(re.search(r"\w+", res).group(0), message)
                        print(full_message)
                        
                        if not "tmi" in full_message:
                            time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                            messages.append("{0}:{1}: {2}".format(time, re.search(r"\w+", res).group(0), message))
        except UnicodeDecodeError as ex:
            print('*'*20)
            print(ex)
            response = 0
            print('*'*20)
        #sleep(0.1)


def save():
    with open("channels/" + cfg.CHANNEL +'.txt', 'a', encoding='utf8') as fp:
            for msg in messages:
                try:
                    fp.write('\n'+msg)
                except Exception as ex:
                    print(msg + " CAN'T BE WRITTEN")
                    print(ex)
                    
    print("-"*10)
    print("SAVED {} MESSAGES".format(len(messages)))
    print("-"*10)


def save_messages(sleep_time):
    global messages
    while running:
        if len(messages) != 0:
            save()
            messages = []

        sleep(sleep_time)

s = socket.socket()
chat_thread = threading.Thread(target=read_chat, )
save_thread = threading.Thread(target=save_messages, args=(cfg.SAVE_TIME, ))
check_online_thread = threading.Thread(target=check_online, )
ignore_offline = False

if __name__ == "__main__":
    main()