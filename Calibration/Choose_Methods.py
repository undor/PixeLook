import tkinter as tk
from tkinter import Canvas


class Configuration:
    def __init__(self):
        self.master = tk.Tk()
        self.box = Canvas(self.master, width=350, height=200)
        self.box.pack()
        self.box.focus_set()
        self.var = tk.IntVar()
        self.model_method = "Null"
        self.convert_method = "Null"
        self.button_a = tk.Button(self.master, text="Full Face Solution", command=lambda: self.ff())
        self.button_b = tk.Button(self.master, text="Head Pose Solution", command=lambda: self.hp())
        self.button_a.place(relx=0.25, rely=0.5, anchor="c")
        self.button_b.place(relx=0.75, rely=0.5, anchor="c")

    def wait_key(self):
        self.button_a.wait_variable(self.var)

    def ff(self):
        self.model_method = "FullFace"
        self.var.set(1)

    def hp(self):
        self.model_method = "HeadPose"
        self.var.set(1)

    def trigonometric(self):
        self.convert_method = "Trigonometric"
        self.var.set(1)

    def linear(self):
        self.convert_method = "Linear"
        self.var.set(1)

    def config_convert(self):
        self.wait_key()
        return self.model_method, self.convert_method

    def config_model(self):
        self.wait_key()
        self.button_a.config(text="Linear Convert", command=lambda: self.linear())
        self.button_b.config(text="Trigonometric Convert", command=lambda: self.trigonometric())
        self.config_convert()





