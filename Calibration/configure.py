import tkinter as tk
from tkinter import Canvas


class Configuration:
    def __init__(self):
        self.master = tk.Tk()
        self.box = Canvas(self.master, width=400, height=200)
        self.box.pack()
        self.box.focus_set()
        self.var = tk.IntVar()
        self.screen_size = 14
        self.name = "Default Name"
        self.button_a = tk.Button(self.master, font="MSGothic 10")
        self.button_b = tk.Button(self.master, font="MSGothic 10")
        self.button_a.place(relx=0.25, rely=0.5, anchor="c")
        self.button_b.place(relx=0.75, rely=0.5, anchor="c")
        self.text = self.box.create_text((200, 20), font="MSGothic 12", fill="red")
        self.e1 = 0

    def wait_key(self):
        self.button_a.wait_variable(self.var)

    def set_size(self):
        size = self.e1.get()
        if size != "":
            self.screen_size = float(size)
        self.var.set(1)

    def config_screen_size(self):
        self.e1 = tk.Entry(self.master)
        self.box.create_window((200, 150), window=self.e1)
        self.button_a.config(text='Insert your screen size in inch', command=lambda: self.set_size())

    def config_model(self):
        self.button_a.place(relx=0.5, rely=0.25, anchor="c")
        self.box.delete("all")
        self.config_screen_size()
        self.wait_key()
        self.box.delete("all")
        self.button_a.destroy()
        self.box.delete("all")
        self.box.destroy()
        self.master.destroy()
        return self.screen_size
