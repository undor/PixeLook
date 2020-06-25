import tkinter as tk
from tkinter import Canvas
from enum import Enum

WAIT_FOR_LEFT = 0
LEFT_CALIBRATION = 1
WAIT_FOR_RIGHT = 2
RIGHT_CALIBRATION = 3
WAIT_FOR_UP = 4
UP_CALIBRATION = 5
WAIT_FOR_DOWN = 6
DOWN_CALIBRATION = 7
WAIT_FOR_CENTER = 8
CENTER_CALIBRATION = 9
FINISH_CALIBRATION = 10


class Stages:
    def __init__(self, **kwargs):
        self.cur_stage = 0

    def next_step(self):
        if self.cur_stage != FINISH_CALIBRATION:
            self.cur_stage = self.cur_stage+1


my_stages = Stages()


def key(event):
    print("pressed", repr(event.char))
    my_stages.next_step()


# def show_text(self):
#     print(self.w.itemcget(self.obj_id, 'text'))


class FullScreenApp(object):
    def __init__(self, **kwargs):
        self.master = tk.Tk()
        pad = 3
        self._geom = '200x200+0+0'
        self.master.attributes('-fullscreen', True)
        self.master.bind('<Escape>', self.toggle_geom)
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        self.w = Canvas(self.master)
        self.w.focus_set()
        self.w.bind("<Key>",   key)
        self.w.pack(fill="both", expand=True)
        # self.obj_id = self.w.create_text(200, 300, text="press again")
        # self.w.bind("<Key>", show_text(self))

    def toggle_geom(self,event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def update_window(self):
        self.master.update()

    def print_pixel(self, pixel):
        delta = 3
        self.w.focus_set()
        self.w.create_rectangle(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#272AEB")

