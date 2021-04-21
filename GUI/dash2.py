#!/usr/bin/python3
import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk() # create a Tk root window
root.geometry('800x480+800+0')
root.attributes("-fullscreen", True)
root.bind("<F11>", lambda event: root.attributes("-fullscreen",
                                    not root.attributes("-fullscreen")))
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))


path = "/home/pi/SCADA_2021/GUI/speedometer.jpg"
img = ImageTk.PhotoImage(Image.open(path))
panel = tk.Label(root, image = img)

panel.pack(side = "bottom", fill = "both", expand = "yes")

root.mainloop() # starts the mainloop

