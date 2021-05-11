#!/usr/bin/python3
import tkinter as tk 
from tkinter import *
from tkinter import ttk 
import sys, os

config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)
import redis
import config
import yaml
import collections
import time
import psycopg2
import database


import datetime
from collections import defaultdict
## for reset button
import subprocess as sub

# # creates instance of Redis
redis_data = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# # creates Publish/Subscribe Redis object called 'p'
p = redis_data.pubsub()
# # p subscribes to get messages
p.subscribe('logs')

# # create Postrgres database cursor
# #  a cursor is like a dummy user in a database that executes commands and retrieves results




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
        label.grid(row = 0, column = 1,  sticky = "w")

        back_page = self.controller.numOfPages
        print("back page" + str(back_page))

        filePath2 = '/usr/etc/scada/GUI/prevPageButton2.png'
        img2 = PhotoImage(file = filePath2)  
        prev_page_button = tk.Button(self, image = img2, command = lambda: self.controller.show_frame(back_page -1 ))
        prev_page_button.image=img2
        prev_page_button.grid(row = 0, column = 1, sticky= "e")
        

        # for logs 
        # os.system('tail -n 100 /var/log/syslog | grep scada')
        p = sub.Popen(["sudo", "scada", "logs"],stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        self.text = Text(self)
        self.text.grid(row = 2, column = 1, sticky= "w")
        self.text.insert(END, output)

        ## contents fo logs redis channel 

        #self.pollFromPostgres()
    

    def pollFromPostgres(self):
        logArray = database.getAllLogs() 
        for row in logArray:
            print("watcher" + str(row[1])+ ":" + str(row[0]))
            logtext = "watcher" + str(row[1])+ ":" + str(row[0])
            self.text.insert(END, logtext)

          
    

