#!/usr/bin/python3


##############################################################################################
## Company: FSAE Lafayette College                                                               
## Engineers: Lia Chrysanthopoulos, Harrison Walker, Irwin Frimpong, Mithil Shah, Adam Tunnell                                    
## Last Updated : 05/10/2021 02:32:17 PM                         
## Project Name: SCADA FSAE 2021                                 
## Module Name: MainGUI.py                                                 
## Description: This is the Main class for the GUI folder. This class is used to run the GUI 
##              using the command python3 MainGUI.py 
##              This class handles which page to display on the screen and hold instances of 
##              every GUI class.           
##                   
#############################################################################################


import tkinter as tk
from tkinter import *
from tkinter import ttk
import threading
import os, sys
os.environ["SDL_FBDEV"] = "/dev/fb0"


lib_path = '/usr/etc/scada/GUI'
sys.path.append(lib_path)

from GUI_Setup import GUISetup
from LogsGUI import LogsGUI
config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

import config
import yaml
import collections
import database
import redis
import ctypes  # for screen size

redis_data = redis.Redis(host='localhost', port=6379, db=0)
# creates Publish/Subscribe Redis object called 'p'
p = redis_data.pubsub()
#subscribes object to logger
p.subscribe('logger_data')



LARGE_FONT = ("Times New Roman", 12)



class Main_GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # #call method to set up dual display
        # self.setSDLVariable()
        
        self.numOfPages = 0

        self.currValues = {}

        self.display_vars = {
            "frames" : {}
        }


        self.screenWidth = self.winfo_screenwidth() # Get current width of canvas
        self.screenHeight = self.winfo_screenheight() # Get current height of canvas
        self.geometry("800x480+0+0")
        
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

        print ("before thread ")
        #this calls all the methods needed to initialize and continuously poll data
        self.initializeCurrValues()
        thread = threading.Thread(target=self.pollFromRedis(), args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
        
        print ("after thread ")

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
        

        # create logs page for last page
        Logsframe = LogsGUI(self.container, self, i)
        self.frames[i] = Logsframe
        Logsframe.grid(row=0, column=0, sticky="nsew")
        self.display_vars["frames"][i] = self.frames[i]
        
        
        self.show_frame(0)


        
            

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

    def initializeCurrValues(self):
        for sensor in config.get('Sensors'):
            self.currValues[sensor] = database.getData(sensor)

    def pollFromRedis(self):
        print("pollfromredis")
        while True:
            message = p.get_message() 
            #print("message: " + str(message))
            ## message = sensor:value
            if (message and (message['data'] != 1 )):
                [sensor_key, sensor_value] = self.splitMsg(message['data'])
                self.currValues[sensor_key] = sensor_value
    
    ## This method splits the sting from the postgres channel into sensorValue and sensorKey 
    def splitMsg(self, message): 
        print("split msg ")
        split_msg = message.split(b":",1)
        
        sensor_valueOLD= split_msg[1]
        #print("sensor_valueOLD: " + str(split_msg[1]))
        sensor_keyOLD = split_msg[0]
        #print("sensor_keyOLD " + str(split_msg[0]))

        # remove the random b in the beginging of string
        sensor_value = sensor_valueOLD.decode('utf-8')
        sensor_key = sensor_keyOLD.decode('utf-8')

        return [sensor_key, sensor_value]

   ## Method to seet os environment variables for dual display
    
    # def setSDLVariable(self):
    #     driver = 'fbturbo'
    #     print("setting up vars")
    #     os.environ["SDL_FBDEV"] = "/dev/feb0"
    #     os.environ["SDL_VIDEODRIVER"] = driver
    #     print("done")


app = Main_GUI()
app.mainloop()