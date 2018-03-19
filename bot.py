import sys
import cfg
import utils
import socket
import re
import threading
from time import sleep

messages = []
running = False

def main():
    global running
    if len(sys.argv) == 1:
        print("Input channel name")
        return 
    
    running = True
    chat_thread.start()
    save_thread.start()
    while True:
        if input() == "exit":
            running = False
            print("Stopping the bot")
            chat_thread.join()
            print("Chat thread is stopped")
            save_thread.join()
            print("Saving thread is stopped")
            save()
            print("Quiting...")
            sys.exit()


def read_chat():
    cfg.CHANNEL = sys.argv[1]
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN #{}\r\n".format(cfg.CHANNEL).encode("utf-8"))

    ###Thread for writing messages to the file every [arg] seconds

    chat_message = re.compile(r":?\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    while running:
        response = s.recv(2048).decode("utf-8")
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
                        messages.append("{0}: {1}".format(re.search(r"\w+", res).group(0), message))
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


chat_thread = threading.Thread(target=read_chat, )
save_thread = threading.Thread(target=save_messages, args=(cfg.SAVE_TIME, ))
if __name__ == "__main__":
    main()