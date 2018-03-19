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

messages = []
running = False

def main():
    if len(sys.argv) == 1:
        print("Input channel name")
        return 
    
    headers = {
        'Client-ID' : CLIENT_ID,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }

    data = requests.get("https://api.twitch.tv/kraken/users?login=" + sys.argv[1], headers=headers).json()
    
    global streamer_id
    streamer_id = data['users'][0]['_id']
    
    stream_data = requests.get("https://api.twitch.tv/kraken/streams/" + streamer_id, headers=headers).json()
    
    
    
    global ignore_offline

    if stream_data['stream'] is None:
        print("Stream is offline, continue anyway Y/N")
        if input() == "N":
            return
        ignore_offline = True

    global running
    running = True
    chat_thread.start()
    save_thread.start()

    while True:
        if input() == "exit":
            running = False

        if running == False:
            print("Stopping the bot")
            chat_thread.join()
            print("Chat thread is stopped")
            save_thread.join()
            print("Saving thread is stopped")
            save()
            if (check_online_thread.is_alive())
                check_online_thread.join()
            print("Quiting...")
            sys.exit()


def check_online():
    headers = {
        'Client-ID' : CLIENT_ID,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }

    global streamer_id
    global running
    while True:
        stream_data = requests.get("https://api.twitch.tv/kraken/streams/" + streamer_id, headers=headers).json()
        if stream_data['stream'] is None:
            print("Streamer has gone offline, finishing...")
            running = False
        sleep(60)
        

def read_chat():
    cfg.CHANNEL = sys.argv[1]
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(cfg.CHANNEL).encode("utf-8"))

    ###Thread for writing messages to the file every [arg] seconds

    chat_message = re.compile(r":?\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

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
        sleep(0.1)


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
        save()
        messages = []

        sleep(sleep_time)

streamer_id = 0
chat_thread = threading.Thread(target=read_chat, )
save_thread = threading.Thread(target=save_messages, args=(cfg.SAVE_TIME, ))
check_online_thread = threading.Thread(target=check_online, )
ignore_offline = False

if __name__ == "__main__":
    main()