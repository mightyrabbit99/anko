import tkinter as tk
from tkinter import messagebox
from frames import *
import os

import traceback


def show_error(self, *args):
  err = traceback.format_exception(*args)
  messagebox.showerror('Exception', err)

tk.Tk.report_callback_exception = show_error

exe_path = os.path.dirname(os.path.abspath(__file__))

class GUI:
  def __init__(self, title="generator"):
    self._title = title
    self.window = self.get_window()

  def get_window(self):
    window = tk.Tk()
    window.title(self._title)
    img = tk.Image("photo", file=os.path.join(exe_path, "../resources/icon1.png"))
    window.tk.call('wm','iconphoto', window._w, img)

    tab_control = NotebookFrame(window)
    tab_control.set_tab_generators(
        [("Prompter", PrompterFrame), ("Searcher", SearcherFrame), ("Anki", AnkiFrame)])
    tab_control.add_new_content_tab()
    tab_control.pack(expand=1, fill=tk.BOTH)

    menubar = NotebookMenubar()
    menubar.render_menu([("File", [("Exit", window.destroy), ("Open", lambda e: None), ("Save as", lambda e: None)])])
    window.config(menu=menubar)

    shortcut_keys = ['<F2>', '<F3>', '<F4>', '<F5>', '<F6>', '<Control-s>']

    def gen_handler(key):
      return lambda e: tab_control.sel_f.action_handler.shortcut_key_press_handler(e, key)

    for k in shortcut_keys:
      window.bind(k, gen_handler(k))

    window.bind('<Alt-F4>', lambda e: window.destroy())

    window.bind('<Control-Tab>', lambda e: tab_control.select_next_tab())
    window.bind('<Control-Shift-Tab>', lambda e: tab_control.select_prev_tab())
    window.bind('<Control-t>', lambda e: tab_control.add_new_content_tab())
    window.bind('<Control-F4>', lambda e: None if tab_control.del_tab()
                is not None else window.destroy())
    return window

  def on_closing(self):
    self.window.destroy()

  def run(self):
    self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    self.window.mainloop()
