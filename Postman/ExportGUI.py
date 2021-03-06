#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: ExportGUI.py                                                 
## Description: Class that allows the user to export data from a current session in Postgres 
##              by filling out fields for each sensor, and export file path. 
##              Data is exported into a EXCEL file for user convience.                
#############################################################################################

import sys, os
import tkinter as tk 
from tkinter import *
from tkinter import ttk 

import collections

import time
from datetime import datetime
lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
sys.path.append(config_path)

import Extract_Data
import Export_Data

import config

MED_FONT = ("Times New Roman", 14)

# Needed to use tk.Frame in order to make a new window!!!
class ExportGUI_Frame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        

        self.controller = controller
        #self.parent = parent 

        self.screenWidth = 900
        self.screenHeight = 900
        
        self.container = tk.Frame(self, width = self.screenWidth, height = self.screenHeight)

        self.winfo_toplevel().title("Export Settings")

        ## classs specific varibles
        self.row_place = 0 
        self.chosenSensors = []
        self.sensorList = []

        pathLabel = tk.Label(self, text = "File Path: ", font= MED_FONT)
        pathLabel.grid(row = 20, column = 0,  sticky = "w")

        defaultPath = "C:/Users/adamd/OneDrive/Documents/School/Car/SCADA_2021/Postman"

        self.pathEntryBox = tk.Entry(self, width = 30)
        self.pathEntryBox.insert(0, defaultPath)
        self.pathEntryBox.grid( row = 20, column = 1)

        fileNameLabel = tk.Label(self, text = "File Name: ", font= MED_FONT)
        fileNameLabel.grid(row = 21, column = 0,  sticky = "w")

        # datetime object containing current date and time
        self.updateTime()
        
        samplePeriodLabel = tk.Label(self, text = "Note: Sample Period cannot be smaller than 1ms ", font= MED_FONT)
        samplePeriodLabel.grid(row = 22, column = 0,  sticky = "w")

        samplePeriodLabel = tk.Label(self, text = "Sample Period (in seconds): ", font= MED_FONT)
        samplePeriodLabel.grid(row = 23, column = 0,  sticky = "w")

        self.samplePeriodLabelEntryBox = tk.Entry(self, width = 20)
        self.samplePeriodLabelEntryBox.grid( row = 23, column = 1)

        extractDataButton = tk.Button(self, text="Export Data", command = lambda: self.exportData()) 
        extractDataButton.grid(row = 23, column = 20)

        self.getSensors()
        self.addSensor()


    # Method gets list of sensors from the config file and stores them in sensorList 
    def getSensors(self): 
        config.load(forceLoad=True)
        yahurd = config.get('Sensors')

        for sen in yahurd:
            self.sensorList.append(sen)

    ## Method creates drop down menu and allows user to select 
    ## Muliple sensors to be exported
    def addSensor(self): 

        SENSORS = self.sensorList
        var = StringVar(self)
        var.set("---") # default value

        self.sensorMenu = OptionMenu(self, var, *SENSORS)
        self.sensorMenu.grid(row = self.row_place, column = 0)

        self.addSensorButton = tk.Button(self, text="Add Sensor", command = lambda: self.saveVars(var.get())) 
        self.addSensorButton.grid(row = self.row_place, column = 1)

        self.row_place = self.row_place + 1

    # Method saves currently selected variables on GUI before exporting 
    def saveVars(self, listvariable):

        if(listvariable == "---"):
            self.popup_msg("User Must Select a Sensor from List")
            
        else: 
            self.addSensorButton.destroy()
            print("varGet : " + str(listvariable))
            self.chosenSensors.append(listvariable)

            #disable changes to currently selected sensors 
            self.sensorMenu.configure(state="disabled")
            #update the time for the fileName 
            self.updateTime()
            self.addSensor()


    ## Method calls export data method from Export_Data Class 
    def exportData(self):

        # update the time for the fileName
        self.updateTime()
        fileName = self.fileNameEntryBox.get()
        samplePeriod = self.samplePeriodLabelEntryBox.get()

        ## Fail Safe Checks
        if not self.samplePeriodLabelEntryBox.get():
            self.popup_msg("Sample Period Field is Empty!")
        elif not self.fileNameEntryBox.get():
            self.popup_msg("File Name Field is Empty!")
        elif not self.pathEntryBox.get():
            self.popup_msg("File Path Field is Empty!")
        elif not self.chosenSensors: 
            self.popup_msg("User Must Select Sensors")
        
        else:
            print(str(fileName))
            print(str(samplePeriod))
            timestampBegin = self.controller.cheapSummaryVars["sessionStart"] 
            print(str(timestampBegin))

            timestampBegin = self.controller.cheapSummaryVars["sessionStart"] 
            timeStampEnd = self.controller.cheapSummaryVars["sessionEnd"] 
            samplePeriod = self.samplePeriodLabelEntryBox.get()
            fileName = self.fileNameEntryBox.get()
            sensorDataList = [] 
            for i in self.chosenSensors:
                sensorData = Extract_Data.getSensorData(i, timestampBegin,timeStampEnd)
                sensorDataList.append(sensorData)
            
            Export_Data.export(self.chosenSensors, sensorDataList, timestampBegin, timeStampEnd, int(samplePeriod),  fileName)
            self.popup_msg("Export Complete!")



##--------- HELPER METHODS---------------------------------------
    # Displays popup window for error handling and fail saves
    def popup_msg(self, msg):
        popup = tk.Tk()
        popup.wm_title("!")

        label = tk.Label(popup, text=msg, font=MED_FONT)
        label.grid(row=0, column = 3)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.grid(row = 3, column = 3)
 
 
    # Helper method to update the time for the fileName to most recent time before exporting 
    def updateTime(self): 
         #update the time for the fileName 
        self.now = datetime.now()
        self.dt_string = self.now.strftime("%d_%m_%Y_%H_%M_%S")
        self.fileNameEntryBox = tk.Entry(self, width = 30)
        self.fileNameEntryBox.insert(0, self.dt_string)
        self.fileNameEntryBox.grid( row = 21, column = 1)




    
## For tesing 
# app = ExportGUI()
# app.mainloop()