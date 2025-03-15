import tkinter as tk


class TabController:
  def set_title(self, title):
    pass

  def get_title(self):
    return ""


class ActionHandler:
  def __init__(self):
    self.tab_controller = None

  def shortcut_key_press_handler(self, e):
    pass

  def set_tab_controller(self, controller: TabController):
    pass


class TabFrame(tk.Frame):
  def get_controller(self):
    return TabController()

  def render(self):
    pass
