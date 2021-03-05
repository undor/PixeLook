import tkinter as tk
from tkinter import Canvas

from UtilsAndModels.Defines import *
from PIL import Image


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
        self.counter = 0

        # if want to use another photo, convert it (code at defines) and make it a tk photo image. then add to button
        self.calib_photo = tk.PhotoImage(file="Calibration/morty_eyes.ppm")
        self.end_calib_photo = tk.PhotoImage(file="Calibration/morty_happy.ppm")
        self.recalibrate_photo = tk.PhotoImage(file="Calibration/morty_angry.ppm")
        self.exit_photo = tk.PhotoImage(file="Calibration/morty_exit.ppm")
        self.wait_photo = tk.PhotoImage(file="Calibration/morty_happy.ppm")

        self.var = tk.IntVar()
        self.button = tk.Button(self.master, text="#", image=self.calib_photo, command=lambda: self.var.set(1))
        self.second_button = tk.Button(self.master, text="I'm satisfied with the result", command=lambda: self.setvar())
        self.text_box = 0
        self.finish = False


    def print_calib_stage(self, stage):
        s = "Current stage number: " + str(stage) + "\n Please look on the "
        if stage == 0:
            self.text_box = self.w.create_text((850, 120), text="Starting Calibration",
                                               font="MSGothic 20 bold", fill="#652828")
            my_text = s + "left Morty"
        elif stage == 1:
            my_text = s + "upper left Morty"
        elif stage == 2:
            my_text = s + "upper Morty"
        elif stage == 3:
            my_text = s + "upper right Morty"
        elif stage == 4:
            my_text = s + "right Morty"
        elif stage == 5:
            my_text = s + "downer right Morty"
        elif stage == 6:
            my_text = s + "downer Morty"
        elif stage == 7:
            my_text = s + "downer left Morty"
        elif stage == 8:
            my_text = s + "center Morty"
        elif stage == 9:
            self.w.itemconfig(self.text_box, text="Check your calibration points")
            self.button.place(relx=0.25, rely=0.5, anchor="c")
            self.button.config(text="I want to Recalibrate", image=self.recalibrate_photo, compound="left")
            self.second_button.place(relx=.75, rely=.5, anchor="c")
            self.second_button.config(image=self.end_calib_photo, compound="left")
            return
        else:
            my_text = " "
        x = stage_dot_locations[stage][0]
        y = stage_dot_locations[stage][1]
        self.button.place(relx=x, rely=y, anchor="c")
        self.w.itemconfig(self.text_box, text=my_text)

    def setvar(self):
        self.finish = True
        self.var.set(1)

    def move_button_to_pixel(self, pixel):
        self.w.focus_set()
        self.button.place_forget()
        self.button.place(x=pixel[0], y=pixel[1], anchor="c")
        self.master.update()

    def arrange_live_draw(self):
        self.button.place(relx=0.25, rely=0.5, anchor="c")
        self.button.config(text="Click to re-Draw")
        self.second_button.place(relx=.75, rely=.5, anchor="c")
        self.second_button.config(text="Click to Exit")
        self.wait_key()
        self.button.place_forget()
        self.second_button.place_forget()
        self.counter = 0
        self.w.delete("all")
        self.master.update()

    def only_exit_button(self):
        self.button.place_forget()
        self.second_button.place(relx=.5, rely=.5, anchor="c")
        self.second_button.config(text="Click to Exit", image=self.exit_photo, compound="left")
        self.wait_key()
        self.second_button.place_forget()
        self.counter = 0
        self.w.delete("all")
        self.master.update()

    def print_pixel(self, pixel, colour=None,clear_prev=False):
        if(clear_prev):
            self.w.delete("all")
            self.master.update()
        delta = 15
        self.w.focus_set()
        if colour is not None:
            self.w.create_oval(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill=colour)
        else:
            self.w.create_oval(pixel[0], pixel[1], pixel[0] + delta, pixel[1] + delta, fill="#FF0000")
        self.counter += 1
        self.master.update()
        return pixel

    def print_calib_points(self, center, colour=None):
        perimeter = 24
        radius = 0.5*perimeter
        if colour is None:
            self.w.create_oval(center[0], center[1], center[0] + perimeter, center[1] + perimeter, fill="#FF0000")
        else:
            self.w.create_oval(center[0], center[1], center[0] + perimeter, center[1] + perimeter, fill=colour)

        self.w.create_text((center[0]+radius, center[1]+radius), text="center dot",
                           font="MSGothic 8 bold", fill="#652828")

    def wait_key(self):
        self.button.wait_variable(self.var)

    def post_process(self, precent=0, process_name="Getting Pixels from video"):
        if self.finish:
            self.post_text_box = self.w.create_text((850, 120), text="", font="MSGothic 20 bold", fill="#652828")
            self.master.update()
            self.finish = False
        self.w.itemconfig(self.post_text_box, text="Postprocess. \n {} \n {:.2f}%".format(process_name, precent))
        self.master.update()