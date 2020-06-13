from __future__ import division
import random
import itertools
from prettytable import PrettyTable
import tkinter as tk
import sys, os
from utils import *

class Game():

    def __init__(self, 
                 memory=[0.5, 0.6, 0.7, 0.8, 0.9, 0.93, 0.95, 0.97, 0.99], \
                 level=[1, 2, 3, 4],                                       \
                 ensemble_min_score=[5]):

        # initialize
        self.history = HistoryColl()
        self.memory = memory
        self.level = level
        self.ensemble_min_score = ensemble_min_score
        self.output = random.choice(list(beat.keys()))

        self.models_inp = [MarkovChain('input_oriented', beat, i[0], i[1]) for i in itertools.product(self.level, self.memory)]
        self.models_out = [MarkovChain('output_oriented', beat, i[0], i[1]) for i in itertools.product(self.level, self.memory)]
        self.models_ens = [Ensembler('ensemble', beat, i) for i in self.ensemble_min_score]

        self.models = self.models_inp + self.models_out + self.models_ens

        # generate game window
        self.window = tk.Tk()
        self.window.geometry("460x400")
        self.window.title("Rock Paper scissorss Game") 

        self.user_win_count = 0.0
        self.bot_win_count = 0.0
        self.draw_count = 0.0
        self.total = 1

        button1 = tk.Button(text="       Rock       ",bg="skyblue",command=self.__rock)
        button1.grid(column=0,row=0)
        button2 = tk.Button(text="       Paper      ",bg="pink",command=self.__paper)
        button2.grid(column=1,row=0)
        button3 = tk.Button(text="      Scissors    ",bg="lightgreen",command=self.__scissors)
        button3.grid(column=2,row=0)
        button4 = tk.Button(text="       Exit       ",bg="red",command=self.__escape)
        button4.grid(column=3,row=0)

        self.window.bind("<Left>", self.__rock)
        self.window.bind("<Up>", self.__paper)
        self.window.bind("<Right>", self.__scissors)
        self.window.bind("<Escape>", self.__escape)


    def launch(self):
        self.window.mainloop()

    # match my bot and user
    def match(self, user_command=''):
        if len(self.history.history) == 10:

            self.history.hist_collector(user_command, self.output)

            max_score = 0

            for model in self.models:

                if model.type in ('input_oriented', 'output_oriented'):
                    key_hist, inp_latest, out_latest = self.history.create_keys_hist(model.level)
                    key_curr = self.history.create_keys(model.level)

                if model.prediction != '':
                    model.update_score(user_command, beat[model.prediction])

                if model.type == 'input_oriented':
                    model.update_matrix(key_hist, inp_latest)

                elif model.type == 'output_oriented':
                    model.update_matrix(key_hist, out_latest)

                elif model.type == 'ensemble':
                    for mod in self.models:
                        if mod.type in ('input_oriented', 'output_oriented'):
                            model.update_matrix(mod.matrix[mod.last_updated_key], model.score)

                if model.type in ('input_oriented', 'output_oriented'):
                    predicted_input = model.predict(key_curr)
                elif model.type == 'ensemble':
                    predicted_input = model.predict()

                if model.score > max_score:
                    best_model = model
                    max_score = model.score
                    self.output = beat[predicted_input]

            if max_score < 1:
                self.output = random.choice(list(beat.keys()))
            
            return self.output

        else:
            self.history.hist_collector(user_command, self.output)
            self.output = random.choice(list(beat.keys()))
            return self.output

    # button action
    def __rock(self, event=None):
        user_command = 'R'
        bot_command = self.output
        self.__result(user_command, bot_command)
        self.output = self.match(user_command)

    def __paper(self, event=None):
        user_command = 'P'
        bot_command = self.output
        self.__result(user_command, bot_command)
        self.output = self.match(user_command)

    def __scissors(self, event=None):
        user_command = 'S'        
        bot_command = self.output
        self.__result(user_command, bot_command)
        self.output = self.match(user_command)

    def __escape(self, event=None):
        exit()

    def __result(self, user_command,bot_command):
        # print overall result
        s = ""
        s += "Round : " + str(self.total) + "\n"
        s += "Bot   : " + str(self.output) + "\n"
        s += "You   : " + str(user_command) + "\n"

        r = judge(user_command, bot_command)

        if r=='U': 
            self.user_win_count+=1   
        elif r=='B':
            self.bot_win_count+=1
        else:
            self.draw_count+=1

        t = PrettyTable(['Player', 'Win Rate'])
        t.add_row(['You', round(self.user_win_count/self.total,2)])
        t.add_row(['Bot', round(self.bot_win_count/self.total,2)])
        t.add_row(['Guardian of probabilty', round(self.draw_count/self.total,2)])
        
        s += str(t)

        text_area = tk.Text(master=self.window,height=20,width=50,bg="#FFFF99")
        text_area.grid(column=0,row=4, columnspan=4) 
        text_area.insert(tk.END,s)

        self.total += 1

game = Game()
game.launch()



    


