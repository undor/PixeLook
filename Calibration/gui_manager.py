import tkinter as tk
from tkinter import Canvas
from enum import Enum


def key(event):
    from Calibration.calibration import calibration_manager
    calibration_manager.flag = 1

class FullScreenApp(object):
    def __init__(self, **kwargs):
        self.master = tk.Tk()
        # TODO: pad?
        pad = 3
        self._geom = '200x200+0+0'
        self.master.attributes('-fullscreen', True)
        self.master.bind('<Escape>', self.toggle_geom)
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        self.w = Canvas(self.master)
        self.w.focus_set()
        self.w.bind("<Key>", key)
        self.w.pack(fill="both", expand=True)
        self.text_box = self.w.create_text((610, 120), text="Starting calibration",
                                           font="MSGothic 20 bold", fill="#652828")
        self.counter = 0

        self.var = tk.IntVar()
        self.button = tk.Button(self.master, text="Click Me", command=lambda: self.var.set(1))
        self.button.place(relx=.5, rely=.5, anchor="c")

    def print_stage(self, stage):
        if stage == 0:
            my_text = "Current stage number: ", stage, "Please look on the left dot"
        elif stage == 2:
            my_text = "Current stage number: ", stage, "Please look on the right dot"
        elif stage == 4:
            my_text = "Current stage number: ", stage, "Please look on the upper dot"
        elif stage == 6:
            my_text = "Current stage number: ", stage, "Please look on the lower dot"
        elif stage == 8:
            my_text = "Current stage number: ", stage, "Please look on the center dot"
        elif stage == 10:
            # TODO: enter here option to go to stage 0 again
            my_text = "Check your calibration points. If you are satisfied,please press <KEY>. else,fuck you meanwhile."
        elif stage == 11:
            # my_text = "left calibration point: ", self.left_gaze_for_debug
            my_text = "Finished Calibrating, start drawing"
        else:
            my_text = ""
        self.w.itemconfig(self.text_box, text=my_text)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def update_window(self):
        if self.counter == 10:
            self.w.delete("all")
            self.counter = 0
        self.master.update()

    def print_pixel(self, pixel):
        delta = 5
        self.w.focus_set()
        self.w.create_rectangle(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#272AEB")
        self.counter += 1

    def print_calib_points(self, up, down, left, right, center):
        perimeter = 24
        radius = 0.5*perimeter
        self.w.focus_set()
        self.w.create_oval(up[0],   up[1], up[0]+perimeter, up[1]+perimeter,  fill="#FF0000")
        self.w.create_text((up[0]+radius, up[1]+radius), text="upper dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(down[0], down[1], down[0] + perimeter, down[1] + perimeter, fill="#FF0000")
        self.w.create_text((down[0]+radius, down[1]+radius), text="lower dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(left[0], left[1], left[0] + perimeter, left[1] + perimeter, fill="#FF0000")
        self.w.create_text((left[0]+radius, left[1]+radius), text="left dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(right[0], right[1], right[0] + perimeter, right[1] + perimeter, fill="#FF0000")
        self.w.create_text((right[0]+radius, right[1]+radius), text="right dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(center[0], center[1], center[0] + perimeter, center[1] + perimeter, fill="#FF0000")
        self.w.create_text((center[0]+radius, center[1]+radius), text="center dot",
                           font="MSGothic 8 bold", fill="#652828")

    def wait_key(self):
        self.button.wait_variable(self.var)

