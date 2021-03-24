# DO WE NEED SHEEBANG?
import tkinter as tk 
from tkinter import *
from tkinter import ttk 

config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)
#import config
import yaml
import collections
import redis
import time
import sys, os
import datetime
import Extract_Data
# import database

# data = redis.Redis(host='localhost', port=6379, db=0)

LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")


class CheapGUI(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        
        
        self.dropDownMenu()
        self.listBox()

        ## get cheap summary data 
        Extract_Data.initialize_database('139.147.91.186')
        Extract_Data.getDelimiter()
        timeData = Extract_Data.getTimeStamps()
        self.timeStampList = timeData[0]
        self.durationList = timeData[1]


        



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


    def listBox(self): 
        # create scroll bar
        my_scrollbar = Scrollbar(self, orient = VERTICAL)
        my_scrollbar.grid(column=2,row=7,  sticky= "ns")
       
        # create list box for session entries
        #my_listbox = tk.Listbox(self, exportselection=False)
        my_listbox = Listbox(self, yscrollcommand = my_scrollbar.set )
        
        # configure scroll bar to list box
        my_scrollbar.config(command= my_listbox.yview)

        my_listbox.grid(column= 1, row = 7)
        my_listbox.bind("<<ListboxSelect>>", self.show_entry)
        

        # added sessions to list for TESTING PURPOSES
        my_list = ["--"]

        for i in range(len(self.timeStampList)):
            my_list.append( str(self.timeStampList[i][0]) +  ' until ' + str(self.timeStampList[i][1]) + ' duration: ' + str(self.durationList[i]))

        # while i < 20:
        #     my_list.append("newSesh")
        #     i= i+ 1
        
        for item in my_list: 
            my_listbox.insert(END, item)


    ## sets and shows the session clicked on by user
    def show_entry(self, event):
        listbox = event.widget
        index = listbox.curselection()
        value = listbox.get(index[0])
        self.controller.cheapSummaryVars["session"] = value
        print(value)


   


    ## this method will remove sessions from the session box displayed on screen 
    ## depeding on which option the user selected frmo the options menu
    def updateScreen(self, filterVar): 
        
        # set the filterBy varriable 
        self.controller.cheapSummaryVars["filterBy"] = filterVar
        print(str(self.controller.cheapSummaryVars["filterBy"]))
        self.showCheapDescription()

        # add condition statements depending on filterVar
        # ...


    #method to show the texual cheap description 
    def showCheapDescription(self):
        # moreDetailsButton = tk.Button(self, text="Okay", command = lambda: self.controller.new_frame("ExpensiveGUI"))
        # moreDetailsButton.grid(row = 3, column = 3)
        
        ## NOTEE: you need () at the end of the method command !!!!
        moreDetailsButton = tk.Button(self, text="Show Details", command = lambda: self.controller.new_window()) 

        moreDetailsButton.grid(row = 3, column = 4)




