#!/usr/bin/python3

##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: CheapSummary_GUI.py                                                 
## Description: This class shows the first window that displays when you run the postman program.             
##              Windows shows all sessions that are logged in postgres database.                
#############################################################################################

import sys, os
import tkinter as tk 
from tkinter import *
from tkinter import ttk 


import collections

import time
lib_path = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(lib_path, 'config')
sys.path.append(config_path)

import config

import datetime
import Extract_Data


# data = redis.Redis(host='localhost', port=6379, db=0)

LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")


class CheapGUI(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.winfo_toplevel().title("Cheap Summary")
        self.my_list = []

        ip_address = config.get("Post_Processing").get("ip_address")
        ## get cheap summary data 
        Extract_Data.initialize_database(ip_address)
        Extract_Data.getDelimiter()
        timeData = Extract_Data.getTimeStamps()
        self.timeStampList = timeData[0]
        self.durationList = timeData[1]

        self.dropDownMenu()
        self.listBox()
        #print("HERE")


    ## Create drop down menu for filtering options 
    def dropDownMenu(self): 
        OPTIONS = [
            "Last Hour",
            "1 Day",
            "1 Week", 
            "1 Year", 
            "All"
        ] 
        var = StringVar(self)
        var.set("---") # default value

        filterMenu = OptionMenu(self, var, *OPTIONS)
        filterMenu.grid(row = 0, column = 0)

        filterButton = tk.Button(self, text="Filter", command = lambda: self.updateScreen(var.get()))
        filterButton.grid(row = 0, column = 1, sticky = "w")

        ## LIA  move this up here on may 11
        
        moreDetailsButton = tk.Button(self, text="Show Details", command = lambda: self.controller.new_window()) 
        moreDetailsButton.grid(row = 3, column = 4)



    # Creates list box for timeStamps 
    def listBox(self): 
        # create scroll bar
        my_scrollbar = Scrollbar(self, orient = VERTICAL)
        my_scrollbar.grid(column=2,row=7,  sticky= "ns")
       
        # create list box for session entries
        my_listbox = Listbox(self, yscrollcommand = my_scrollbar.set, width=55)
        
        # configure scroll bar to list box
        my_scrollbar.config(command= my_listbox.yview)

        my_listbox.grid(column= 1, row = 7)
        my_listbox.bind("<<ListboxSelect>>", self.show_entry)
    

        for i in range(len(self.timeStampList)):
            self.my_list.append( str(self.timeStampList[i][0]) + '           '+'Duration: ' + str(self.durationList[i]))

        
        for item in self.my_list: 
            my_listbox.insert(END, item)


    ## Method sets and shows the session clicked on by user
    def show_entry(self, event):
        listbox = event.widget
        index = listbox.curselection()
        value = listbox.get(index[0])
        item = self.my_list.index(value)
        #print("ITEM: " + str(item))

        sessionTimeStamps = self.timeStampList[item]
        self.controller.cheapSummaryVars["session"] = value
        self.controller.cheapSummaryVars["sessionStart"] = sessionTimeStamps[0]
        self.controller.cheapSummaryVars["sessionEnd"] = sessionTimeStamps[1]

        
        # print("timestamp: " + str(sessionTimeStamps))
        # print(value)


   


    ## Method will remove sessions from the session box displayed on screen 
    ## depeding on which option the user selected frmo the options menu
    def updateScreen(self, filterVar): 
        
        # set the filterBy varriable 
        self.controller.cheapSummaryVars["filterBy"] = filterVar
        print(str(self.controller.cheapSummaryVars["filterBy"]))
        #self.showCheapDescription()

        # add condition statements depending on filterVar
        # ...
        # if filterVar == "Last Hour":
        # elif filterVar == "1 Day":
        # elif filterVar == "1 Week":
        # elif filterVar == "1 Year":
        
                        
        # moreDetailsButton = tk.Button(self, text="Show Details", command = lambda: self.controller.new_window()) 
        # moreDetailsButton.grid(row = 3, column = 4)






