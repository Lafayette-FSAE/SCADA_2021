import tkinter as tk 
from tkinter import *
from tkinter import ttk 
import tkinter.ttk

import config
import yaml
import collections
import config
import redis
import time
import sys, os
import datetime

data = redis.Redis(host='localhost', port=6379, db=0)
columns = config.get('Display')


LARGE_FONT = ("Verdana", 12)
class RealTimeDisplay(tk.Frame):

    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.view_label = self.controller.display_vars["sort_by_data"]

        #self.get_data(self.controller.display_vars["checkBox_label"])
        #self.dispay_gui()

        # doIt = tk.Button(self, text = "DO IT", fg = "black", command = lambda: self.display_gui2())
        # doIt.grid(row = 0, column = 0, sticky = "nsew")

        doIt = tk.Button(self, text = "DO IT", fg = "black", command = lambda: self.get_data(controller))
        doIt.grid(row = 0, column = 0, sticky = "nsew")
        
        MainMenu = tk.Button(self, text = "Main Menu", fg = "black", command = lambda: self.controller.home_button("MainMenu"))
        MainMenu.grid(row = 0, column = 3, sticky = "nsew")



    def display_gui2(self):
        # for i in self.controller.display_vars["checkBox_label"]:
        # label = tk.Label(self, text = str(self.controller.display_vars["sort_by_data"]), font= LARGE_FONT )
        # label.grid(row = 0, column = 0, sticky = "nsew")
        #print("view label " + self.view_label)
       # self.get_data(self.view_label)

        time = datetime.datetime.now().strftime("Time: %H:%M:%S")

        # label = tk.Label(self, text = str(time), font= LARGE_FONT )
        # label.grid(row = 0, column = 10, sticky = "nsew")

        label = tk.Entry(self, width = 20)
        label.insert(0,str(time) )
        label.grid(column = 1, row = 2)

        self.after(1000, self.display_gui2) # run itself again after 1000 ms





    def get_data(self, controller):

        column_spot = 0 
        box_spot = 1
        for k in self.controller.display_vars["checkBox_label"]:
            dataType = k
            print("view label " + str(k))


            print("made it")
            config.load(forceLoad=True)
            self.sensorDict = config.get('Sensors')

            count = 0
            for sensor in self.sensorDict:
                attributeDict = self.sensorDict[sensor]
                num_of_rows = 0 
                for key in attributeDict:
                    #print(str(attributeDict.get(key))) # gets the actual name 
                    #print("key " + key) # gets the key 
                    #print("data" + str(data))
                    #print(data.get('ouput_target'))
                    
                    if(attributeDict.get(key) == dataType ):
                        label1 = tk.Label(self, text = str(attributeDict.get(key)), font= LARGE_FONT )
                        label1.grid(row = 0, column = column_spot, sticky = "nsew")

                        print("STRING SENSOR" + str(attributeDict.get('output_target')))
                        label = tk.Label(self, text = str(attributeDict.get('output_target')), font= LARGE_FONT )
                        label.grid(row = 2 + count, column = column_spot, sticky = "nsew")

                        entry_ = tk.Entry(self, width = 20)
                        entry_.insert(0, "Nada for now")
                        entry_.grid( row = 2 + count, column = box_spot)
                        num_of_rows = num_of_rows + 1
                        count = count + 1
                        
       # tkinter.ttk.Separator(self, orient=VERTICAL).grid(column=3, row=0, rowspan=10, sticky='ns')

                        
                       
            column_spot= column_spot + 2
            box_spot = box_spot +2

        self.display_gui2()







    
