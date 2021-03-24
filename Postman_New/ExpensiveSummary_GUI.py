#!/usr/bin/python3
import sys, os
import tkinter as tk 
from tkinter import *
from tkinter import ttk 

config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)
#import config
# import yaml
import collections
# import redis
import time
import datetime
# import database

# data = redis.Redis(host='localhost', port=6379, db=0)

LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")


class ExpensiveGUI(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.screenWidth = 700
        self.screenHeight = 700

        self.container = tk.Frame(self, width = self.screenWidth, height = self.screenHeight)

        ## TEST DisplayText 
        label = tk.Label(self, text = " YES ", font= TITLE_FONT)
        label.grid(row = 0, column = 2,  sticky = "e")

        filterButton = tk.Button(self, text="Filter", command = lambda: self.updateScreen(var.get()))
        filterButton.grid(row = 0, column = 4, sticky = "w")


