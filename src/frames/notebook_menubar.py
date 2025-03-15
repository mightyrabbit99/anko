import tkinter as tk

MAX_TAB_TITLE_LEN = 20

class NotebookMenubar(tk.Menu):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def render_menu(self, options):
    for name, choices in options:
      mn = tk.Menu(self, tearoff=0)
      for choice in choices:
        if choice is None:
          mn.add_separator()
        else:
          mn.add_command(label=choice[0], command=choice[1])
      self.add_cascade(label=name, menu=mn)
