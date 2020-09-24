import tkinter as tk
from tkinter import Canvas


class FullScreenApp(object):
    def __init__(self):
        self.master = tk.Tk()
        self._geom = '200x200+0+0'
        self.master.attributes('-fullscreen', True)
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()
        self.w = Canvas(self.master)
        self.w.focus_set()
        self.w.pack(fill="both", expand=True)
        # self.text_box = self.w.create_text((610, 120), text="Starting calibration",
        # font="MSGothic 20 bold", fill="#652828")
        self.counter = 0

        self.var = tk.IntVar()
        self.button = tk.Button(self.master, text="Click to Capture", command=lambda: self.var.set(1))
        self.second_button = tk.Button(self.master, text="I'm satisfied with the result", command=lambda: self.setvar())
        self.text_box = 0
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
        if self.counter == 150:
            self.w.delete("all")
            self.counter = 0
        self.master.update()

    def print_capture_button(self, pixel):
        print("putting button in: ", pixel[0], pixel[1])
        self.button.place(x=pixel[0], y=pixel[1], anchor="c")
        self.button.config(text="Click to Capture")

    def print_pixel(self, pixel):
        delta = 5
        self.w.focus_set()
        self.w.create_oval(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#FF0000")
        self.counter += 1
        self.update_window()
        return pixel

    def print_calib_points(self, center):
        perimeter = 24
        radius = self.width*0.1
        self.w.create_oval(self.width/2 - radius, self.height/2 - radius, self.width/2 + radius, self.height/2 + radius,
                           fill="#FFFFFF")
        radius = 0.5*perimeter
        self.w.create_oval(center[0], center[1], center[0] + perimeter, center[1] + perimeter, fill="#FF0000")
        self.w.create_text((center[0]+radius, center[1]+radius), text="center dot",
                           font="MSGothic 8 bold", fill="#652828")

    def wait_key(self):
        self.button.wait_variable(self.var)
