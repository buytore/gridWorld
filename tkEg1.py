#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode Tkinter tutorial

This script shows a simple window
on the screen.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""

from Tkinter import *
from ttk import Style, Button


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="blue")

        self.parent = parent
        self.parent.title("MarkB")
        self.pack(fill=BOTH, expand=1)
        self.centerWindow()

        self.initUI()

    def initUI(self):
        self.parent.title("Quit button")
        self.style = Style()
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)

        quitButton = Button(self, text="Quit", command=self.quit)
        quitButton.place(x=50, y=50)

    def centerWindow(self):
        w = 290
        h = 150
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()


if __name__ == '__main__':
    main()