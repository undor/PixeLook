import tkinter as tk
from tkinter import Canvas


# def key(event):
#     print("doing nothing")


class FullScreenApp(object):
    def __init__(self):
        self.master = tk.Tk()
        # pad = 3
        self._geom = '200x200+0+0'
        self.master.attributes('-fullscreen', True)
        # self.master.bind('<Escape>', self.toggle_geom)
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        self.w = Canvas(self.master)
        self.w.focus_set()
        # self.w.bind("<Key>", key)
        self.w.pack(fill="both", expand=True)
        # self.text_box = self.w.create_text((610, 120), text="Starting calibration",
                                           # font="MSGothic 20 bold", fill="#652828")
        self.counter = 0

        self.var = tk.IntVar()
        self.button = tk.Button(self.master, text="Click to Capture", command=lambda: self.var.set(1))
        self.second_button = tk.Button(self.master, text="I'm satisfied with the results", command=lambda: self.setvar())

        self.finish = False

    # def toggle_geom(self, event):
    #     geom = self.master.winfo_geometry()
    #     print(geom, self._geom)
    #     self.master.geometry(self._geom)
    #     self._geom = geom

    def print_calib_stage(self, stage):
        if stage == 0:
            self.text_box = self.w.create_text((610, 120), text="Starting calibration",
                                               font="MSGothic 20 bold", fill="#652828")
            my_text = "Current stage number: ", stage, "Please look on the left dot"
            self.button.place(relx=0.035, rely=0.5, anchor="c")
        elif stage == 2:
            my_text = "Current stage number: ", stage, "Please look on the right dot"
            self.button.place(relx=0.965, rely=0.5, anchor="c")
        elif stage == 4:
            my_text = "Current stage number: ", stage, "Please look on the upper dot"
            self.button.place(relx=0.5, rely=0.035, anchor="c")
        elif stage == 6:
            my_text = "Current stage number: ", stage, "Please look on the lower dot"
            self.button.place(relx=0.5, rely=0.965, anchor="c")
        elif stage == 8:
            my_text = "Current stage number: ", stage, "Please look on the center dot"
            self.button.place(relx=0.5, rely=0.5, anchor="c")
        elif stage == 10:
            my_text = "Check your calibration points"
            self.button.place(relx=0.25, rely=0.5, anchor="c")
            self.button.config(text="Click to Recalibrate")
            self.second_button.place(relx=.75, rely=.5, anchor="c")
        else:
            my_text = " "
        self.w.itemconfig(self.text_box, text=my_text)

    def setvar(self):
        self.finish = True
        self.var.set(1)

    def update_window(self):
        if self.counter == 15:
            self.w.delete("all")
            self.counter = 0
        self.master.update()

    def print_pixel(self, pixel):
        delta = 5
        self.w.focus_set()
        self.w.create_rectangle(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#272AEB")
        self.counter += 1
        self.update_window()

    def print_calib_points(self, up, down, left, right, center):
        perimeter = 24
        radius = 0.5*perimeter
        self.w.create_oval(up[0],   up[1], up[0]+perimeter, up[1]+perimeter,  fill="#FF0000")
        self.w.create_text((up[0]+radius, up[1]+radius), text="upper dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(down[0], down[1], down[0] - perimeter, down[1] - perimeter, fill="#FF0000")
        self.w.create_text((down[0]+radius, down[1]+radius), text="lower dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(left[0], left[1], left[0] + perimeter, left[1] + perimeter, fill="#FF0000")
        self.w.create_text((left[0]+radius, left[1]+radius), text="left dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(right[0], right[1], right[0] - perimeter, right[1] - perimeter, fill="#FF0000")
        self.w.create_text((right[0]+radius, right[1]+radius), text="right dot",
                           font="MSGothic 8 bold", fill="#652828")
        self.w.create_oval(center[0], center[1], center[0] + perimeter, center[1] + perimeter, fill="#FF0000")
        self.w.create_text((center[0]+radius, center[1]+radius), text="center dot",
                           font="MSGothic 8 bold", fill="#652828")

    def wait_key(self):
        self.button.wait_variable(self.var)
