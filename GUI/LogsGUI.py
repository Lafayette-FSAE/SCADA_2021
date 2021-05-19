#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: LogsGUI.py                                                 
## Description: Class to setup the layout of GUI that displays the Error Logs. This is the last 
##              page of the GUI display. Error logs include watcher logs and scada logs. 
##              Watcher logs are pulled from Postgres database and represent sensor errors.  l
##              Scada Logs printed from the terminal using the command "sudo scada logs". 
##              These logs contain errors from the service files.              
##                   
#############################################################################################

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

        filePath2 = '/usr/etc/scada/GUI/prevPageButton2.png'
        img2 = PhotoImage(file = filePath2)  
        prev_page_button = tk.Button(self, image = img2, command = lambda: self.controller.show_frame(back_page -1 ))
        prev_page_button.image=img2
        prev_page_button.grid(row = 0, column = 1, sticky= "e")
        

        # for logs 
        p = sub.Popen(["sudo", "scada", "logs"],stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        self.text = Text(self)
        self.text.grid(row = 2, column = 1, sticky= "w")
        self.text.insert(END, output)

        ## contents for logs redis channel 
        self.pollFromPostgres()
    

    def pollFromPostgres(self):
        logArray = database.getAllLogs() 
        for row in logArray:
            logtext = "watcher " + str(row[1])+ " : " + str(row[0]) + "\n"
            self.text.insert(END, logtext)

          
    

