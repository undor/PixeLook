import tkinter as tk
from tkinter import Canvas
from enum import Enum


def key(event):
    from Calibration.calibration import calibration_manager
    calibration_manager.next_step()

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
        self.text_box= self.w.create_text((410, 120), text="Starting calibration", font="MSGothic 20 bold", fill="#652828")


    def print_stage(self,stage):
        my_text = "now on stage number: " , stage
        self.w.itemconfig(self.text_box, text=my_text)

    def toggle_geom(self,event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def update_window(self):
        self.master.update()

    def print_pixel(self, pixel):
        delta = 5
        self.w.focus_set()
        self.w.create_rectangle(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#272AEB")

