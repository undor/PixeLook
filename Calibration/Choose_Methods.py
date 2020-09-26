import tkinter as tk
from tkinter import Canvas


class Configuration:
    def __init__(self):
        self.master = tk.Tk()
        self.box = Canvas(self.master, width=400, height=200)
        self.box.pack()
        self.box.focus_set()
        self.var = tk.IntVar()
        self.model_method = "Null"
        self.convert_method = "Null"
        self.screen_size = 13.3
        self.name = "Default Name"
        self.button_a = tk.Button(self.master, font="MSGothic 10")
        self.button_b = tk.Button(self.master, font="MSGothic 10")
        self.button_a.place(relx=0.25, rely=0.5, anchor="c")
        self.button_b.place(relx=0.75, rely=0.5, anchor="c")
        self.text = self.box.create_text((200, 20), font="MSGothic 12", fill="red")
        self.e1 = 0

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

    def set_size(self):
        size = self.e1.get()
        if size != "":
            self.screen_size = float(size)
        self.var.set(1)

    def set_name(self):
        name = self.e1.get()
        if name != "":
            self.name = str(name)
        self.var.set(1)

    def config_screen_size(self):
        self.e1 = tk.Entry(self.master)
        self.box.create_window((200, 150), window=self.e1)
        self.button_a.config(text='Insert your screen size in inch', command=lambda: self.set_size())

    def config_name(self):
        self.e1 = tk.Entry(self.master)
        self.box.create_window((200, 150), window=self.e1)
        self.button_a.config(text='Insert your name', command=lambda: self.set_name())

    def config_model(self):

        self.box.itemconfig(self.text, text="Choose your model method")
        self.button_a.config(text="Full Face Solution", command=lambda: self.ff())
        self.button_b.config(text="Head Pose Solution", command=lambda: self.hp())
        self.wait_key()

        self.box.itemconfig(self.text, text="Choose your pixel converting method")
        self.button_a.config(text="Linear Convert", command=lambda: self.linear())
        self.button_b.config(text="Trigonometric Convert", command=lambda: self.trigonometric())
        self.wait_key()

        self.button_b.destroy()
        self.button_a.place(relx=0.5, rely=0.25, anchor="c")
        self.box.delete("all")
        self.config_screen_size()
        self.wait_key()

        self.box.delete("all")
        self.config_name()
        self.wait_key()

        self.button_a.destroy()
        self.box.delete("all")
        self.box.destroy()
        self.master.destroy()

        return self.model_method, self.convert_method, self.screen_size, self.name
