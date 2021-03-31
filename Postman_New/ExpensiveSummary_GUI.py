#!/usr/bin/python3
import sys, os
import tkinter as tk 
from tkinter import *
from tkinter import ttk 


database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)

lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
sys.path.append(config_path)

import config

import collections

import time
import datetime
import Extract_Data
import statistics

# data = redis.Redis(host='localhost', port=6379, db=0)

LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")


class ExpensiveGUI(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.screenWidth = 700
        self.screenHeight = 700

        self.rowPlace = 0
        self.colPlace = 0

        self.container = tk.Frame(self, width = self.screenWidth, height = self.screenHeight)

        self.winfo_toplevel().title("Expensive Summary:      " + str(self.controller.cheapSummaryVars["session"]) )
        ex_sum_sensors = config.get("Post_Processing").get("expensive_summary_data")
        timeStampBegin = self.controller.cheapSummaryVars["sessionStart"]
        timeStampEnd = self.controller.cheapSummaryVars["sessionEnd"]

        ## TEST DisplayText 
        nameLabel = tk.Label(self, text = "sensor_id", font= TITLE_FONT)
        nameLabel.grid(row = self.rowPlace, column = self.colPlace,  sticky = "w")

        meanLabel = tk.Label(self, text = "mean", font= TITLE_FONT)
        meanLabel.grid(row = self.rowPlace, column = self.colPlace + 1 ,  sticky = "w")
    
        minLabel = tk.Label(self, text = "minimum", font= TITLE_FONT)
        minLabel.grid(row = self.rowPlace, column = self.colPlace + 2,  sticky = "w")

        maxLabel = tk.Label(self, text = "maximum", font= TITLE_FONT)
        maxLabel.grid(row = self.rowPlace, column = self.colPlace + 3,  sticky = "w")

        self.rowPlace = self.rowPlace + 1
        self.colPlace = 0



        for sensor_id in ex_sum_sensors:
            data = Extract_Data.getSensorData(sensor_id, timeStampBegin, timeStampEnd)
            dataValues = [float(item[0]) for item in data]
            mean = statistics.mean(dataValues)
            minimum = min(dataValues)
            maximum = max(dataValues)

        ## TEST DisplayText 
            nameLabel = tk.Label(self, text = str(sensor_id), font= TITLE_FONT)
            nameLabel.grid(row = self.rowPlace, column = self.colPlace,  sticky = "w")

            meanLabel = tk.Label(self, text = str(mean), font= TITLE_FONT)
            meanLabel.grid(row = self.rowPlace, column = self.colPlace + 1 ,  sticky = "w")

            minLabel = tk.Label(self, text = str(minimum), font= TITLE_FONT)
            minLabel.grid(row = self.rowPlace, column = self.colPlace + 2,  sticky = "w")

            maxLabel = tk.Label(self, text = str(maximum), font= TITLE_FONT)
            maxLabel.grid(row = self.rowPlace, column = self.colPlace +3 ,  sticky = "w")

            self.rowPlace = self.rowPlace + 2 
            self.colPlace = 0

        # filterButton = tk.Button(self, text="Filter", command = lambda: self.updateScreen(var.get()))
        # filterButton.grid(row = 0, column = 4, sticky = "w")

        # Detailsbutton = tk.Button(self, image = laf_img, command = lambda: self.controller.new_window())
        # Detailsbutton.grid(row = 0, column = 0, sticky= "w")


