#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import Tkinter
except ImportError:
    import tkinter as Tkinter

from protocol import Proxy

PORT = 1900 # Controller port
PASSWORD = '0123456789'


class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.seqnums = Tkinter.IntVar()
        self.seqnums.set(1)
        self.addressVariable = Tkinter.StringVar()
        self.passwordVariable = Tkinter.StringVar()
        self.serialVariable = Tkinter.StringVar()
        self.serialVariable.set('sdf')
        self.get_proxy()
        self.initialize()

    def get_proxy(self, event=None):
        try:
            pw = self.passwordVariable.get()
            address = self.addressVariable.get()
            if  address in ('<discover>', ''):
                self.proxy = Proxy.discover(pw, PORT, self.seqnums.get())
            else:
                self.proxy = Proxy(pw, PORT, address, self.seqnums.get())
            self.serialVariable.set(self.proxy.serial)
        except:
            self.serialVariable.set('-')

    def initialize(self):
        self.grid()

        self.address = Tkinter.Entry(self,textvariable=self.addressVariable)
        label = Tkinter.Label(self, text='address:')
        label.grid(row = 0, sticky = 'E')
        self.address.grid(row = 0, column = 1, sticky = 'EW')
        self.address.bind("<Return>", self.get_proxy)
        self.addressVariable.set(u"<discover>")

        self.password = Tkinter.Entry(self,textvariable=self.passwordVariable)
        label = Tkinter.Label(self, text='password:')
        label.grid(row = 0, column = 2, sticky = 'E')
        self.password.grid(row = 0, column = 3, sticky = 'EW')
        self.passwordVariable.set(u"123456789")

        self.entryVariable = Tkinter.StringVar()
        self.entry = Tkinter.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=1,sticky='ENSW', columnspan=4)
        self.entry.bind("<Return>", self.OnPressEnter)
        self.entryVariable.set(u"get")

        Tkinter.Label(self, text='serial:').grid(row = 0, column = 4, sticky = 'E')
        self.serial = Tkinter.Label(self, textvariable=self.serialVariable).grid(row = 0, column = 5, sticky = 'W')


        button = Tkinter.Button(self, text=u"Run command", command=self.OnButtonClick)
        button.grid(column=5, row=1)

        self.secnumbutton = Tkinter.Checkbutton(self, text="seqnums", variable=self.seqnums, command=self.OnSecnumClick)
        self.secnumbutton.grid(column=4, row=1, sticky='E')

        self.text = Tkinter.Text(self)
        self.text.grid(column=0, row=2, columnspan=6, sticky='EWNS')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=5)
        self.grid_rowconfigure(2, weight=1)
        self.resizable(True,True)
        self.update()
        self.geometry(self.geometry())
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def OnButtonClick(self):
        self.OnPressEnter(None)

    def OnPressEnter(self,event):
        d = self.entryVariable.get().split(' ')
        if d[0] == 'get':
            if len(d) > 1:
                path = d[1]
            else:
                path = '*'
            self.text.insert(Tkinter.END, '\n'.join(self.proxy.get(path))+'\n\n')
        elif d[0] == 'set':
            if len(d) > 1:
                path = d[1]
                if len(d) > 2:
                    value = d[2]
                else:
                    value = None
            else:
                path = '*'
                value = None
            self.text.insert(Tkinter.END, '\n'.join(self.proxy.set(path, value))+'\n\n')
        self.text.see(Tkinter.END)
        self.entry.focus_set()
        self.entry.selection_range(0, Tkinter.END)

    def OnSecnumClick(self):
        self.get_proxy()

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('NBE UDP protocol test gui')
    app.mainloop()

