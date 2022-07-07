import tkinter as tk

class LabeledEntry(tk.Entry):
    def __init__(self, master=None, label="Search", **kwargs):
        tk.Entry.__init__(self, master, **kwargs)
        self.label = label
        self.on_exit()
        self.bind('<FocusIn>', self.on_entry)
        self.bind('<FocusOut>', self.on_exit)

    def on_entry(self, event=None):
        if self.get() == self.label:
            self.config(fg='black')
            self.delete(0, tk.END)
         
    def on_exit(self, event=None):
        if not self.get():
            self.insert(0, self.label)
            self.config(fg = 'grey')

class LabeledEntryPass(tk.Entry):
    def __init__(self, master=None, label="Search", **kwargs):
        tk.Entry.__init__(self, master, **kwargs)
        self.label = label
        self.on_exit()
        self.bind('<FocusIn>', self.on_entry)
        self.bind('<FocusOut>', self.on_exit)

    def on_entry(self, event=None):
        if self.get() == self.label:
            self.config(fg='black')
            self.delete(0, tk.END)
            self.config(show = '*')
           

    def on_exit(self, event=None):
        if not self.get():
            self.config(show = self.get())
            self.insert(0, self.label)
            self.config(fg = 'grey')

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground