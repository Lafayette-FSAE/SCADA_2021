#!/usr/bin/python3
import sys, os
import tkinter as tk 
from tkinter import *
from tkinter import ttk 

# config_path = '/usr/etc/scada/config'
# sys.path.append(config_path)

# database_path = '/usr/etc/scada/utils'
# sys.path.append(database_path)
#import config
import collections

import datetime

import ctypes  # for screen size
from CheapSummary_GUI import CheapGUI
from ExpensiveSummary_GUI import ExpensiveGUI
from ExportGUI import ExportGUI_Frame


LARGE_FONT = ("Times New Roman", 12)


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)


        self.cheapSummaryVars = {
            "filterBy" : " ",
            "session" : " ",
            "sessionStart" : " ",
            "sessionEnd" : " "
        }
        
        # self.screenWidth = self.winfo_screenwidth() # Get current width of canvas
        # self.screenHeight = self.winfo_screenheight() # Get current height of canvas
        
        self.screenWidth = 700
        self.screenHeight = 700
        

        # set screen to full size 
        self.container = tk.Frame(self, width = self.screenWidth, height = self.screenHeight)
        self.container.grid_propagate(False)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # for F in (CheapGUI, ExpensiveGUI):
        # frame = F(self.container, self)
        frame = CheapGUI(self.container, self)
        self.frames[CheapGUI] = frame
        frame.grid(row=0, column=0, sticky="nsew")
    

        self.show_frame(CheapGUI)


    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()



    # create a new window for Expensive GUI
    def new_window(self):
        self.newWindow = tk.Toplevel(self)
        frame = ExpensiveGUI(self.newWindow, self)
        self.frames[ExpensiveGUI] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        # create a new window for Export Data GUI
    def new_window2(self):
<<<<<<< HEAD
        #self.new_window.destroy()
        self.newWindow = tk.Toplevel(self)
        frame2 = ExportGUI(self.newWindow, self)
        self.frames[ExportGUI] = frame2
        frame2.grid(row=0, column=0, sticky="nsew")
=======
        #self.newWindow.destroy()
        self.newWindow2 = tk.Toplevel(self)
        self.app = ExportGUI_Frame(self.newWindow2, self)
        #frame = ExportGUI_Frame(self.newWindow2, self)
        #self.frames[ExportGUI_Frame] = frame
        #frame.grid(row=0, column=0, sticky="nsew")
>>>>>>> 9fa5892a04168267e726e5cb2334f5829aa4feac


        

app = Main()
app.mainloop()