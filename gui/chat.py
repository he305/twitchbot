import tkinter as tk
from tkinter.filedialog import askopenfilename 
import threading
from time import sleep
from cfg import CLIENT_ID, BACKUP_DEEPNESS
import requests
from tkinter.ttk import Notebook
import datetime
import shutil
import os
from bot import Bot, stop_stream_message
import re

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F1FF-\U0001FFFF"
                           "]+", flags=re.UNICODE)

class Page(tk.Frame):
    def __init__(self, channel, stream_data, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.channel = channel
        self.text = tk.Text(self)
        self.text.grid(row=0, column=0, sticky='NESW')
        self.running = True
        self.messages = []

        self.scrollb = tk.Scrollbar(self, command=self.text.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollb.set

        self.scroll_var = tk.BooleanVar(value=True)
        self.scroll_checkbox = tk.Checkbutton(self, text="Scroll down", onvalue = 1, offvalue = 0, variable=self.scroll_var)
        self.scroll_checkbox.grid(row=1, column=0, sticky=tk.W)

        self.bot = Bot(self.channel, self)
                
        self.paste_stream_start(stream_data)
        
        self.bot_thread = threading.Thread(target=self.run)
        self.bot_thread.start()

        self.save_thread = threading.Thread(target=self.save_messages)
        self.save_thread.start()


    def run(self):
        self.bot.read_chat()


    def stream_finisher(self):
        sleep(10)
        stop_stream_message(self.channel)



    def close_tab(self):
        self.bot.running = False
        self.running = False

        # self.stream_finisher_thread = threading.Thread(target=self.stream_finisher)
        # self.stream_finisher_thread.start()

        self.bot_thread.join()
        print("{} bot stopped".format(self.channel))
        self.save_thread.join()
        self.destroy()

    def paste_stream_start(self, stream_data):
        d = datetime.datetime.strptime(stream_data[0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')
        d = d.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        time = d.strftime("%Y-%m-%d %H-%M-%S")

        message = "{0}:{1}: {2}".format(time, "he305bot", "Stream started")
        
        try:
            with open("channels/" + self.channel +'.txt', 'r+', encoding='utf8') as fp:
                lines = fp.readlines()
                if message.strip() != lines[0].strip():
                    
                    i = BACKUP_DEEPNESS
                    while i >= 0:
                        self.make_backup(i)
                        i -= 1

                    if os.path.isfile("channels/" + self.channel +'_old.txt'): 
                        shutil.copy2("channels/" + self.channel +'_old.txt', "channels/" + self.channel + "_old_old.txt")
                    shutil.copy2("channels/" + self.channel +'.txt', "channels/" + self.channel + "_old.txt")
                    fp.seek(0)
                    fp.truncate()
                    fp.write(message)
                    
        except IOError:
            with open("channels/" + self.channel +'.txt', 'w', encoding='utf8') as fp:
                fp.write(message)
    

    def print_message(self, message):
        try:
            self.text.insert(tk.END, message + '\n')
            if self.scroll_var.get():
                self.text.see(tk.END)
        except Exception:
            try:
                self.text.insert(tk.END, emoji_pattern.sub(r'', message) + '\n')
            except Exception as ex:
                print(ex)
                print("Not emoji, but exception anyway")

    def save(self):
        with open("channels/" + self.channel +'.txt', 'a', encoding='utf8') as fp:
            for msg in self.messages:
                try:
                    fp.write('\n'+msg)
                except Exception as ex:
                    print(msg + " CAN'T BE WRITTEN")
                    print(ex)
        self.print_message('-'*10)
        self.print_message("{}: SAVED {} MESSAGES".format(datetime.datetime.now().strftime('%H:%M:%S'), len(self.messages)))
        self.print_message('-'*10)


    def save_messages(self):
        while self.running:
            if len(self.messages) != 0:
                self.save()
                self.messages = []

            sleep(60)

    def make_backup(self, current):
        if os.path.isfile("channels/{}{}.txt".format(self.channel, '_old'*current)): 
            shutil.copy2("channels/{}{}.txt".format(self.channel, '_old'*current), "channels/{}{}.txt".format(self.channel, '_old'*(current+1)))


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Status: waiting")
        self.geometry('900x500')
        self.tk.call('encoding', 'system', 'utf-8')
        rows = 0
        while rows < 150:
            self.rowconfigure(rows, weight=1)
            self.columnconfigure(rows, weight=1)
            rows += 1
        
        self.load_file_button = tk.Button(self, text="Open streamers file",command=self.load_file).grid(row=0, column=0)

        self.streamers_label = tk.Label(self)
        self.streamers_label.grid(row=1, column=0)
        self.overwatch_thread = threading.Thread(target=self.overwatch)
        self.overwatch_thread.daemon = True

        self.update_status = tk.Label(self)
        self.update_status.grid(row=2, column=0)


        self.frames = Notebook(self)
        self.frames.grid(row=0, column=1, columnspan=150, rowspan=100, sticky='NESW')
        self.pages = []


    def load_file(self):
        fname = askopenfilename(filetypes=(("Text File", "*.txt"),("All Files","*.*")))
        if fname:
            self.load_data(fname)
            return


    def load_data(self, fname):
        with open(fname, 'r', encoding="utf8") as f:
            self.streamers = [s.strip() for s in f.readlines()]
        streamers_str = '\n'.join(self.streamers)

        try:
            os.mkdir('channels')
        except FileExistsError:
            print('Folder already exists')

        self.streamers_label['text'] = "Overwatched streams:\n" + streamers_str
        self.title('Status: working')
        self.overwatch_thread.start()


    def overwatch(self):
        
        headers = {
            'Client-ID' : CLIENT_ID,
            'Accept' : 'application/vnd.twitchtv.v5+json'
        }


        tabs = []
        while True:
            for streamer in self.streamers:
                stream_data = requests.get("https://api.twitch.tv/helix/streams?user_login=" + streamer.replace('_live', ''), headers=headers).json()
                if 'error' in stream_data:
                    sleep(20)
                    continue

                if not stream_data['data'] and '_live' in streamer:
                    
                    print("{} finished streaming, starting process stop".format(streamer.replace('_live', '')))
                    for i, p in enumerate(tabs):
                        if p.channel == streamer.replace('_live', ''):
                            self.frames.forget(i)
                            finded = p
                            p.close_tab()
                            break
                    tabs.remove(finded)

                    print("{} finished streaming".format(streamer.replace('_live', '')))
                    self.streamers[self.streamers.index(streamer)] = streamer.replace('_live', '')

                if stream_data['data'] and not '_live' in streamer:
                    print("{} stream is starting".format(streamer))

                    p = Page(streamer, stream_data['data'], self.frames)
                    self.frames.add(p, text=streamer.replace('_live', ''))
                    tabs.append(p)

                    self.streamers[self.streamers.index(streamer)] = streamer + '_live' 

                streamers_str = '\n'.join(self.streamers)
                self.streamers_label['text'] = "Overwatched streams:\n" + streamers_str
            
            print("Last check: {}".format(datetime.datetime.now().strftime('%H:%M:%S')))
            self.update_status['text'] = "Last check: {}".format(datetime.datetime.now().strftime('%H:%M:%S'))
            sleep(60)
            

if __name__ == "__main__":
    App().mainloop()