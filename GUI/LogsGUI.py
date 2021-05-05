#!/usr/bin/python3
import tkinter as tk 
from tkinter import *
from tkinter import ttk 
import sys, os
config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)
import config
import yaml
import collections
import time


import datetime
from collections import defaultdict
## for reset button
import subprocess as sub




LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")
START_ROW = 1
BOX_WIDTH = 11

class LogsGUI(tk.Frame):
    def __init__(self, parent, controller, pageNum): 
        tk.Frame.__init__(self, parent)
        self.controller = controller


        ## Display Page Number
        label = tk.Label(self, text = "SCADA LOGS ", font= TITLE_FONT)
        label.grid(row = 0, column = 2,  sticky = "e")

        back_page = self.controller.numOfPages
        print("back page" + str(back_page))

        filePath2 = '/usr/etc/scada/GUI/prevPageButton2.png'
        img2 = PhotoImage(file = filePath2)  
        prev_page_button = tk.Button(self, image = img2, command = lambda: self.controller.show_frame(back_page -1 ))
        prev_page_button.image=img2
        prev_page_button.grid(row = 0, column = 1, sticky= "w")
        

        # for logs 
        # os.system('tail -n 100 /var/log/syslog | grep scada')
        p = sub.Popen('sudo scada logs',stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        label_logs = tk.Label(self, text = output, font= TITLE_FONT)
        label.grid(row = 1, column = 0,  sticky = "e")
        ## contents fo logs redis channel 
