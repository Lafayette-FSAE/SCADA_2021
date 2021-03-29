#!/usr/bin/python3
import tkinter as tk
from tkinter import *
from tkinter import ttk
import os, sys
os.environ["SDL_FBDEV"] = "/dev/fb0"


lib_path = '/usr/etc/scada/GUI'
sys.path.append(lib_path)

from GUI_Setup import GUISetup
config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

import config
import yaml
import collections

import ctypes  # for screen size



LARGE_FONT = ("Times New Roman", 12)



class Main_GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # #call method to set up dual display
        # self.setSDLVariable()
        
        self.numOfPages = 0

        self.display_vars = {
            "frames" : {}
        }


        self.screenWidth = self.winfo_screenwidth() # Get current width of canvas
        self.screenHeight = self.winfo_screenheight() # Get current height of canvas
        
        self.attributes('-fullscreen', True)  
        self.fullScreenState = False
        
        ## Press the ESC button to escape out of full screen (Kiosk) mode
        self.bind("<Escape>", self.quitFullScreen)
        

        # set screen to full size 
        self.container = tk.Frame(self, width = self.screenWidth, height = self.screenHeight)

        self.container.grid_propagate(False)

        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        

        self.frames = {}

        
        self.get_pages() #call function to get number of pages to display
        max = self.numOfPages
        i = 0
        #while iterator is less than totalNum of pages 
        while i<max:
            frame = GUISetup(self.container, self, i)
           
            self.frames[i] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            #frame.configure(bg = 'red') #  set background color 
            self.display_vars["frames"][i] = self.frames[i]


            i = i+1
        
        self.show_frame(0)

        thread = threading.Thread(target=self.pollFromRedis, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        
            

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        #frame.getNewData()




    # get the number of pages under the pages categroy
    def get_pages(self): 
        config.load(forceLoad=True)
        self.displayDict = config.get('Display')
        self.pagesNum = self.displayDict.get('Pages')
        self.numOfPages = len(self.pagesNum)

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.attributes("-fullscreen", self.fullScreenState)


    def pollFromRedis(self):
        pass

   ## Method to seet os environment variables for dual display
    
    # def setSDLVariable(self):
    #     driver = 'fbturbo'
    #     print("setting up vars")
    #     os.environ["SDL_FBDEV"] = "/dev/feb0"
    #     os.environ["SDL_VIDEODRIVER"] = driver
    #     print("done")


app = Main_GUI()
app.mainloop()