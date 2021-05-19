#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: ExpensiveSummary_GUI.py                                                 
## Description: This class shows the second window that displays when you run the postman program.             
##              Windows shows the max, min and avg for the session selected in the CheapSumary_GUI.py 
##              window.               
#############################################################################################

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
from ExportGUI import ExportGUI_Frame

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

        self.winfo_toplevel().title("Session Preview:      " + str(self.controller.cheapSummaryVars["session"]) )
        ex_sum_sensors = config.get("Post_Processing").get("session_preview_data")
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


        ## button to go to ExportGUI
        pickSensorButton = tk.Button(self, text = "Export Session" , command = lambda: self.controller.new_window2())
        pickSensorButton.grid(row = 20, column = 18, sticky= "w")


        