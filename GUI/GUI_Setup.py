#!/usr/bin/python3
import tkinter as tk 
from tkinter import *
from tkinter import ttk 

config_path = '/usr/etc/scada/config'
sys.path.append(config_path)

database_path = '/usr/etc/scada/utils'
sys.path.append(database_path)
import config
import yaml
import collections
import redis
import time
import sys, os
import datetime
import database
from collections import defaultdict

redis_data = redis.Redis(host='localhost', port=6379, db=0)
# creates Publish/Subscribe Redis object called 'p'
p = redis_data.pubsub()
#subscribes object to logger
p.subscribe('logger_data')



LARGE_FONT = ("Times New Roman", 12)
TITLE_FONT = ("Times", 14, "bold italic")
START_ROW = 1
BOX_WIDTH = 11

class GUISetup(tk.Frame):
    def __init__(self, parent, controller, pageNum): 
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.name_list = [] ## list of values from output_target attribubte
        self.sensorList = [] # list of sensors to be displayed
        self.coordDict = defaultdict(list) # dictinoary of sensors and their corresponding boxes on screen
        self.unitList = [] # dictinoary of sensors and their corresponding boxes on screen

        self.dataList = [] ## list of current data from each sensor on the screen

        self.entryBoxList = [] ## list on entry boxes diaplyed on screen
        self.column_place = 0
        self.row_place = 0

        self.pageNumber = pageNum

        ## Set the title of the window to the page number 
        self.winfo_toplevel().title("SPARKY")
        
        ## Lafayette LOGO Button 
        display_text = "SCADA Subsystem V-1 \n Class of 2021 \n @Authors \n Lia Chrysanthopoulos, Irwin Frimpong, \n Mithil Shah, Adam Tunnell, \n Harrison Walker"
        laf_filePath ='/usr/etc/scada/GUI/LafayetteSymbol2.png'
        laf_img = PhotoImage(file = laf_filePath)  
        laf_button = tk.Button(self, image = laf_img, command = lambda: self.popup_msg(display_text))
        laf_button.image=laf_img
        laf_button.grid(row = 0, column = 0, sticky= "w")

   
        ## Display Page Number
        label = tk.Label(self, text = "Page " + str(self.pageNumber + 1) , font= TITLE_FONT)
        label.grid(row = 0, column = 2,  sticky = "e")

        curr_page = self.pageNumber +1
        next_frame = self.pageNumber + 1

        # add spaces for asthetic purposes
        self.add_space(13, 4)
        self.add_space(14, 4)


        ## create button image for Next Page
        filePath ='/usr/etc/scada/GUI/nextPageButton2.png'
        img = PhotoImage(file = filePath)  
        next_page_button = tk.Button(self, image = img,  command = lambda: self.controller.show_frame(next_frame))
        next_page_button.image=img
        next_page_button.grid(row = 0, column = 4, sticky = "w")


        if(curr_page >= 2):
            self.add_space(0, 4)
            self.add_space(13, 0)
            self.add_space(14, 0)
            
            filePath2 = '/usr/etc/scada/GUI/prevPageButton2.png'
            img2 = PhotoImage(file = filePath2)  
            prev_page_button = tk.Button(self, image = img2, command = lambda: self.controller.show_frame(curr_page -2))
            prev_page_button.image=img2
            prev_page_button.grid(row = 0, column = 1, sticky= "w")
            next_page_button.destroy()

            if(curr_page != self.controller.numOfPages):

                filePath ='/usr/etc/scada/GUI/nextPageButton2.png'
                img3 = PhotoImage(file = filePath)  
                next_page_button2 = tk.Button(self, image = img3, command = lambda: self.controller.show_frame(next_frame))
                next_page_button2.image=img3
                next_page_button2.grid(row = 0, column = 4, sticky = "w")


        self.get_page_groups(curr_page)
        #self.get_sensor_data()
        self.initial_data_settup()





    def get_page_groups(self, pageNum): 
        config.load(forceLoad=True)
        self.displayDict = config.get('Display')
        self.pageNum = self.displayDict.get('Pages')
        
        # for each group in the Groups list in config.yaml fil e
        for page in self.pageNum:
            
            ## condition checks which page GUI needs to create & display 
            if(page == pageNum):
                
                # reset col for new page
                self.column_place = 0
                #reset row for new page
                self.row_place = START_ROW
                
                ## pass in list of groups under that page 
                self.get_groups(self.pageNum[page])

   
   
    def get_groups(self, groupList):
        self.displayDict = config.get('Display')
        self.groupDict = self.displayDict.get('Groups')
        
        # for the groups listed under the Pages category
        for group in groupList:
            
            # for the groups listed under the Groups category
            for groupName in  self.groupDict:
                
                ## if the Group names are equal 
                if(group == groupName):
                   
                    # display group label
                    group_label = tk.Label(self, text = str(groupName), font= LARGE_FONT, fg = "blue" )
                    group_label.grid(row = START_ROW, column = self.column_place, sticky = "nsew")
                    
                    # for the sensors in the groupName in the Group list 
                    for sensor in self.groupDict[groupName]: 
                        # add the sensor name to sensor List 
                        self.find_group_in_SensorList(sensor)
                
                    # add to column for new group
                    self.column_place = self.column_place + 2
                    #reset row for new group
                    self.row_place = START_ROW


    # MEthod finds matches the sensor names and retrieves the display variable name called var_name
    def find_group_in_SensorList(self, sensorName): 
        self.sensorDict = config.get('Sensors') # listed name of sensors under Sensor in config file 
        
        # for each sensor in the Sensors list  ## COMMENT OUT 2/19          
        #for sen in list(self.sensorDict.keys()): # go though list of sensors to match correct display var

        for sen, val in self.sensorDict.items():

            #print("sen " + str(sen))
            #print("value " + str(val))
            
            if(sen == sensorName):

                ## get the display variable name in config file 
                ## it is labaled var_name
                for key, value in val.items():
                    if( key == "var_name"):
                        display_name = value ## set to display_name 
                        break
                
                # put sensor on screen 
                label = tk.Label(self, text = str(display_name), font= LARGE_FONT )
                placeRow = 1 + self.row_place
                label.grid(row = placeRow, column = self.column_place, sticky = "w")

                #get the unit of the sensor -- look at getUnit method 
                unit = self.getUnit(self.sensorDict.get(sen))
                
                # add to sensor list that holds the sensor name and its place on screen
                self.sensorList.append({'sensor' : sensorName, 'column': self.column_place, 'row': self.row_place, 'unit': unit})                
                # puts keys in dict with no value
                self.coordDict[sensorName] = []

                #self.coordDict[sensorName].append(entry)                
 
                # inriment row for next sensor 
                self.row_place = self.row_place + 1
                # break loop once sensor is found
                break


    # # Method gets the data to display on the screen 
    # def get_sensor_data(self):
        
    #     itr = 0 ## iterator to keep track of name_list index 

    #     # for each sensor in the list of sensors to be displayed
    #     for sensor in self.sensorList:

    #         sensorName = sensor.get('sensor')
    #         value = database.getData(sensorName)

    #         if value is None:
    #             value = 'None'
            
    #         ## Add value to entry box on screen 
    #         entry_ = tk.Entry(self, width = BOX_WIDTH)

    #         ## Display units according to data status
    #         if str(value) == 'no data':
    #             unit = " "
    #         elif sensor.get('unit') is None: 
    #             unit = " "
    #         else:
    #             unit = sensor.get('unit')


    #         text = str(value) + " " + unit
    #         entry_.insert(0, str(text))

    #         # find the corresponding row and column places 
    #         rowPlace = sensor.get('row') + 1
    #         column_place = sensor.get('column') + 1

    #         entry_.grid( row = rowPlace, column = column_place)
            
            
    #         # add the entryBox to the entryBox list 
    #         self.entryBoxList.append(entry_)
    #         # add to dataList 
    #         self.dataList.append(value)
            

    #     ## go to refresh sensor data method
    #     self.refresh_sensors()



     # Method gets the data to display on the screen 
    def initial_data_settup(self):
        
        itr = 0 ## iterator to keep track of name_list index 

         # for each entry in the list of sensors to be displayed
        for sensorEntry in self.sensorList:
            
            ## Add value to entry box on screen 
            entry_ = tk.Entry(self, width = BOX_WIDTH)

            #gets most recent value in database
            sensor = sensorEntry.get('sensor')
            value = database.getData(sensor)
            #entry_.insert(0, str(text))


            ## Display units according to data status
            if str(value) == 'no data':
                unit = " "
            elif sensorEntry.get('unit') is None: 
                unit = " "
            else:
                unit = sensorEntry.get('unit')

            text = str(value) + " " + unit

            #need to make sure entry box is not edit-able
            entry_.configure(state='normal')
            entry_.insert(0, str(text))
            entry_.configure(state='disabled')

            # find the corresponding row and column places 
            rowPlace = sensorEntry.get('row') + 1
            column_place = sensorEntry.get('column') + 1

            entry_.grid( row = rowPlace, column = column_place)
            
            
            # add the entryBox to the entryBox list 
            self.entryBoxList.append(entry_)
            self.coordDict[sensor].append(itr)
            self.unitList.append(unit) # append unit to unit list for use in replace_data_on_screen()

            itr = itr+1
            
        ## go to refresh sensor data method
        self.getNewData()
            


    # ## This method runs on a continuous loop to refresh the sensor data
    # def refresh_sensors(self):
    #     itr = 0 ## iterator for datalist index 

    #     # for a sensors in the list of sensors to be displayed
    #     for sensor in self.sensorList:
    #         old_data = self.dataList[itr]
            
    #         sensorName = sensor.get('sensor')
    #         new_data = database.getData(sensorName)      
    #         # if the data has been updated
    #         if(new_data != old_data):
    #             self.dataList[itr] = new_data
    #             self.placedata_on_screen(itr, new_data, sensor)

    #         #Harry: I put this in for debugging
    #         print('Iterator:' + str(itr))
    #         print('Sensor:' + sensorName )
    #         print('New Data:' + new_data)

    #         itr = itr + 1
    #     # refresh data every 2 s
    #     self.after(5000, self.refresh_sensors)


## This method is recursive in order to update and display changes in data
    def getNewData(self): 

        message = p.get_message() 
        ## message = sensor:value
        if (message and (message['data'] != 1 )):
            [sensor_key, sensor_value] = self.splitMsg(message['data'])

            for coordEntry in self.coordDict[sensor_key]:
                self.placedata_on_screen(coordEntry, sensor_value, sensor_key)

        ## call this method after 1s to refresh data
        self.after(1000, self.getNewData)

      
## This method splits the sting from the postgres channel into sensorValue and sensorKey 
    def splitMsg(self, message): 
        
        split_msg = message.split(b":",1)
        
        sensor_valueOLD= split_msg[1]
        #print("sensor_valueOLD: " + str(split_msg[1]))
        sensor_keyOLD = split_msg[0]
        #print("sensor_keyOLD " + str(split_msg[0]))

        # remove the random b in the beginging of string
        sensor_value = sensor_valueOLD.decode('utf-8')
        sensor_key = sensor_keyOLD.decode('utf-8')

        return [sensor_key, sensor_value]


    
    # this method puts the data on the screen after it has been updated
    def placedata_on_screen(self, listIndex, value, key):
        
        # delete entry box with old information
        self.entryBoxList[listIndex].configure(state='normal')
        self.entryBoxList[listIndex].delete(0, "end")
        self.entryBoxList[listIndex].configure(state='disabled')
       
        if value is None: 
            value = 'None'
        
        unit = self.unitList[listIndex]
        text = str(value) + " " + str(unit)
        
        # insert new data in the entryBox
        self.entryBoxList[listIndex].insert(0, str(text))

   

# HELPER METHODS #
##########################################################################################


    def popup_msg(self, msg):
        popup = tk.Tk()
        popup.wm_title("!")

        label = tk.Label(popup, text=msg, font=LARGE_FONT)
        label.grid(row=0, column = 3)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.grid(row = 3, column = 3)


    def add_space(self, row_, col_):
        label = tk.Label(self, text="      ", font=LARGE_FONT)
        label.grid(row=row_, column = col_, sticky = "e")

    ## proabbly dont need this method
    def getUnit(self, sensor): 
        #key_list = sensor.keys()
        for key, value in sensor.items():
            if(key == "unit"):
                return value
