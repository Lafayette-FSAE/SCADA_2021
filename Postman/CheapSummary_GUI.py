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

from datetime import datetime


# data = redis.Redis(host='localhost', port=6379, db=0)

LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")


class CheapGUI(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        self.winfo_toplevel().title("Session Browser")
        self.my_list = []

        ## for filter button 
        self.newstr1 = ""
        self.newstr2 = ""
        self.currTimeInt = 0
        self.newInt = 0

        ip_address = config.get("Post_Processing").get("ip_address")
        ## get cheap summary data 
        Extract_Data.initialize_database(ip_address)
        Extract_Data.getDelimiter()
        timeData = Extract_Data.getTimeStamps()
        self.timeStampList = timeData[0]
        self.durationList = timeData[1]
        self.value = ""


        self.dropDownMenu()
        self.listBox()

    ## Create drop down menu for filtering options 
    def dropDownMenu(self): 
        OPTIONS = [
            "Last Hour",
            "1 Day",
            "1 Month", 
            "1 Year", 
            "All"
        ] 
        var = StringVar(self)
        var.set("---") # default value

        filterMenu = OptionMenu(self, var, *OPTIONS)
        filterMenu.grid(row = 0, column = 0)

        filterButton = tk.Button(self, text="Filter", command = lambda: self.updateScreen(var.get()))
        filterButton.grid(row = 0, column = 1, sticky = "w")

        moreDetailsButton = tk.Button(self, text="Show Details", command = lambda: self.controller.new_window()) 
        moreDetailsButton.grid(row = 3, column = 4)



    # Creates list box for timeStamps 
    def listBox(self): 
        # create scroll bar
        my_scrollbar = Scrollbar(self, orient = VERTICAL)
        my_scrollbar.grid(column=2,row=7,  sticky= "ns")
       
        # create list box for session entries
        self.my_listbox = Listbox(self, yscrollcommand = my_scrollbar.set, width=55)
        
        # configure scroll bar to list box
        my_scrollbar.config(command= self.my_listbox.yview)

        self.my_listbox.grid(column= 1, row = 7)
        self.my_listbox.bind("<<ListboxSelect>>", self.show_entry)
    
        ## add tiime stamp and duration to session list called my_list 
        for i in range(len(self.timeStampList)):
            self.my_list.append( str(self.timeStampList[i][0]) + '           '+'Duration: ' + str(self.durationList[i]))

        ## add each entry in the textbox on screen 
        for item in self.my_list: 
            self.my_listbox.insert(END, item)


    ## Method sets and shows the session clicked on by user
    def show_entry(self, event):
        listbox = event.widget
        index = listbox.curselection()
        value = listbox.get(index[0])
        item = self.my_list.index(value)
        self.value = value

        sessionTimeStamps = self.timeStampList[item]
        self.controller.cheapSummaryVars["session"] = value
        self.controller.cheapSummaryVars["sessionStart"] = sessionTimeStamps[0]
        self.controller.cheapSummaryVars["sessionEnd"] = sessionTimeStamps[1]


   


    ## Method will remove sessions from the session box displayed on screen 
    ## depeding on which option the user selected frmo the options menu
    def updateScreen(self, filterVar): 
        # Get current time
        now = datetime.now()
        
        # set the filterBy varriable 
        self.controller.cheapSummaryVars["filterBy"] = filterVar

        ## change format of current time string to match session string format 
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S:00000000")


        #  condition statements depending on filterVar
        if filterVar == "Last Hour":
            ## clear textbox just in case prev filter was applied 
            for item in self.my_list:  
                self.my_listbox.delete(0, END)
            ## populate textbox with session from past hour 
            self.getIndex(11, 12, dt_string)

        elif filterVar == "1 Day":
            ## clear textbox just in case prev filter was applied 
            for item in self.my_list:  
                self.my_listbox.delete(0, END)
            ## populate textbox with session from past day 
            self.getIndex(8, 9, dt_string)

        elif filterVar == "1 Month":
            ## clear textbox just in case prev filter was applied 
            for item in self.my_list:  
                self.my_listbox.delete(0, END)
            ## populate textbox with session from past month 
            self.getIndex(5, 6, dt_string)

        elif filterVar == "1 Year":
            ## clear textbox just in case prev filter was applied 
            for item in self.my_list:  
                self.my_listbox.delete(0, END)
            ## populate textbox with session from past year 
            self.getIndex(0, 3, dt_string)
       
        else: 
            ## clear textbox just in case prev filter was applied 
            for item in self.my_list:  
                self.my_listbox.delete(0, END)
            ## populate textbox with all entries 
            for item in self.my_list: 
                self.my_listbox.insert(END, item)

 

    ## method to fill textbox with entires depending on filter variable. 
    def getIndex(self, index1, endIndex1, currTime):

        for oldk in range(len((currTime))):
            k = oldk
            if( k == index1):
                while k < (endIndex1 + 1):
                    self.newstr2 += currTime[k]
                    k = k + 1
        self.currTimeInt = int(self.newstr2)
        ## reset new string 
        self.newstr2 = ""

        for i in range(len(self.timeStampList)):
            stringDT = str(self.timeStampList[i][0])
            for j in range(len(stringDT)):
                if( j == index1):
                    while j < (endIndex1 + 1):
                        self.newstr1 += str(stringDT[j])
                        j = j + 1
            self.newInt = int(self.newstr1)

            if(self.currTimeInt - self.newInt <= 1):
                # print("subtract: " + str(self.currTimeInt - self.newInt))
                ## add entires to textbox that meet condition 
                self.my_listbox.insert(END, self.my_list[i])
            else:
                ## delete entries not met in condition 
                self.my_listbox.delete(0, END)
                
                self.my_listbox.grid(column= 1, row = 7)
            ## reset neew string 
            self.newstr1 = ""
           



