import tkinter as tk
from tkinter import Canvas
from enum import Enum

WAIT_FOR_LEFT = 0
LEFT_CALIBRATION = 1
WAIT_FOR_RIGHT = 2
RIGHT_CALIBRATION = 3
WAIT_FOR_CENTER = 4
CENTER_CALIBRATION = 5
FINISH_CALIBRATION = 6

class stages():
    def __init__(self, **kwargs):
        self.cur_stage=0

    def next_step(self):
        if(self.cur_stage!=FINISH_CALIBRATION):
            self.cur_stage=self.cur_stage+1

my_stages=stages()

def key(event):
    print("pressed", repr(event.char))
    my_stages.next_step()


class FullScreenApp(object):
    def __init__(self, **kwargs):
        self.master= tk.Tk()
        pad=3
        self._geom='200x200+0+0'
        self.master.attributes('-fullscreen', True)
        self.master.bind('<Escape>',self.toggle_geom)
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        self.w = Canvas(self.master)
        self.w.focus_set()
        self.w.bind("<Key>",   key)
        self.w.pack(fill="both", expand=True)



    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

    def update_window(self):
        self.master.update()


    def print_pixel(self,pixel):
        delta = 4
        self.w.focus_set()
        self.w.create_rectangle(pixel[0], pixel[1], pixel[0]+ delta, pixel[1]+ delta, fill="#272AEB")





