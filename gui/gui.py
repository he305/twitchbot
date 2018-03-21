import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter import simpledialog
import fileinput
from emotes import emotes_global, emotes_bttv_global, emotes_channels
import os
import requests
import glob
import datetime
from collections import Counter
from graph import get_dynamic

emotes_all = []

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

    return codes


class Message:
    def __init__(self, nickname, time, message, channel):
        self.nickname = nickname
        self.time = time
        self.message = message
        self.channel = channel
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

        while "@" +  self.channel in self.emotes: 
            self.emotes.remove("@" + self.channel)

        while "@" +  self.channel in self.words:
            self.words.remove("@" + self.channel)


    def __lt__(self, other):
         return self.time < other.time


    def __str__(self):
        return "{}:{}".format(self.nickname, self.message)


    def count_emote(self, emote):
        return self.emotes.count(emote)



class ChooseEmoteDialog(tk.Tk):
    def __init__(self, emotes, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Choose emote")
        self.parent = parent
        self.list = tk.Listbox(self)
        for msg in emotes:
            self.list.insert(tk.END, msg)
        print(emotes)
        self.list.grid(row=0, column=0, columnspan=3)
        self.scrollb = tk.Scrollbar(self, command=self.list.yview)
        self.scrollb.grid(row=0, column=3, sticky='nsew')
        self.list['yscrollcommand'] = self.scrollb.set

        self.delta_var = tk.BooleanVar()
        self.delta_checkbox = tk.Checkbutton(self, text="Delta", onvalue = 1, offvalue = 0, variable=self.delta_var)
        self.delta_checkbox.grid(row=1, column=1, sticky=tk.W)

        self.button = tk.Button(self, text="Accept", command=self.show_graph).grid(row=1, column=0)
        self.quit = tk.Button(self, text="Quit", command=self._close).grid(row=1, column=2)


    def show_graph(self):
        if not self.list.get(tk.ACTIVE):
            return

        get_dynamic(self.list.get(tk.ACTIVE), self.parent.messages, self.delta_var.get())


    def _close(self):
        self.destroy()


class Output(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.widgets()

    def widgets(self):
        self.text = tk.Text(self)
        self.text.grid(row=0, column=0)

        self.text.insert(tk.END, "Welcome to twich messages analyzer\n")
        self.text.insert(tk.END, "Open txt file using button at the left, format is:\n")
        self.text.insert(tk.END, "time:login:message\n")
        self.text.insert(tk.END, "Compatibility with other bots rather than he305bot is not promised\n")


        self.scrollb = tk.Scrollbar(self, command=self.text.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollb.set
        self.clear_button = tk.Button(self, text="Clear text", command=self.clear_text).grid(row=1, column=0, sticky=tk.E)

    def show_message(self, message, clear=False):
        if clear:
            self.clear_text()
        self.text.insert(tk.END, message)
        self.text.insert(tk.END, '\n')


    def clear_text(self):
        self.text.delete('1.0', tk.END)


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.messages = []
        self.title("Analyzer")
        
        #Buttons
        self.load_file_button = tk.Button(self, text="Open file", command=self.load_file)
        self.load_file_button.grid(row=0, column=0, sticky=tk.W + tk.N)

        self.show_smiles_button = tk.Button(self, text="Top smiles", state=tk.DISABLED, command=self.show_smiles)
        self.show_smiles_button.grid(row=2, column=0, sticky=tk.W)

        self.show_words_button = tk.Button(self, text="Top words", state=tk.DISABLED, command=self.show_words)
        self.show_words_button.grid(row=2, column=1, sticky=tk.W)

        self.show_graph_button = tk.Button(self, text="Show graph", state=tk.DISABLED, command=self.show_graph)
        self.show_graph_button.grid(row=3, column=0, columnspan=2)

        self.window = Output(self)
        self.window.grid(row=1, column=3, sticky=tk.E)


    def load_file(self):
        fname = askopenfilename(filetypes=(("Text File", "*.txt"),("All Files","*.*")))
        if fname:
            self.channel = os.path.basename(fname).replace('_old', '').replace('.txt', '')
            self.window.show_message("Loading messages, please wait...", True)
            self.load_data(fname)
            return

    def load_data(self, fname):
        with open(fname, 'r', encoding="utf8") as f:
            data = f.readlines()

        self.window.text.delete('1.0', tk.END)

        global emotes_all    
        emotes_all = emotes_global + emotes_bttv_global + get_bttv_local(self.channel) + get_ffz_local(self.channel) 
        print(get_bttv_local(self.channel)) 

        self.messages = []
        self.words = []
        self.emotes = []
        self.nicknames = []

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
            
            self.messages.append(Message(nickname, time, message, self.channel))

        for msg in self.messages:
            self.words += msg.words
            self.emotes += msg.emotes
            self.nicknames.append(msg.nickname)
        

        self.window.show_message(str(len(self.messages)) + " messages loaded", True)
        self.show_smiles_button['state'] = 'normal'
        self.show_words_button['state'] = 'normal'
        self.show_graph_button['state'] = 'normal'
        
    def show_smiles(self):
        top = 20
        self.window.show_message("Top {} channel emotes\n{}".format(top, "-"*20))
        c = Counter(self.emotes)
        c = c.most_common(int(top))
        for emote in c[:top]:
            self.window.show_message("{} : {}".format(emote[0], emote[1]))

    def show_words(self):
        top = 20
        self.window.show_message("Top {} most used words\n{}".format(top, "-"*20))
        c = Counter(self.words)
        c = c.most_common(int(top))
        for word in c[:top]:
            self.window.show_message("{} : {}".format(word[0], word[1]))


    def show_graph(self):
        top = 20
        c = Counter(self.emotes)
        c = c.most_common(int(top))
        emote_list = []
        for emote in c[:top]:
            emote_list.append(emote[0])

        choose = ChooseEmoteDialog(emote_list, self)
        
if __name__ == "__main__":
    App().mainloop()