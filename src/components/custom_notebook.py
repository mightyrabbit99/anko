import tkinter as tk
from tkinter import ttk

from core.utils import when_failed
import bisect

class CustomNotebook(ttk.Notebook):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.frame_id_map_tab_id = {}  # id(frame) -> '@..:..'
    self.tab_id_map_no = {}  # '@..:..' -> no
    self.unused_no = []
    self.tab_id_map_frame = {}  # '@..:..' -> frame

    self.right_clicked_tab_id = None
    self.tab_popup_menu = tk.Menu(self, tearoff=0)
    self.tab_popup_menu.add_command(
        label="Delete", command=self.del_tab)
    self.bind("<Button-3>", self.popup)
    self.bind("<FocusOut>", lambda e: self.reset())

    self.dragged_tab_id = None
    self.bind("<ButtonPress-1>", self.on_drag_start)
    self.bind("<B1-Motion>", self.on_dragging)
    self.bind("<ButtonRelease-1>", self.on_drag_drop)

  def reset(self):
    self.right_clicked_tab_id = None

  @when_failed(-1)
  def index(self, *args, **kwargs):
    return super().index(*args, **kwargs)
  
  def tab_id(self, index):
    return self.tabs()[index]

  def popup(self, event):
    no = self.index("@%d,%d" % (event.x, event.y))
    if no < 0:
      self.right_clicked_tab_id = None
      return False
    self.right_clicked_tab_id = self.tab_id(no)
    try:
      self.tab_popup_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
      self.tab_popup_menu.grab_release()
      return True

  def on_drag_start(self, event):
    no = self.index("@%d,%d" % (event.x, event.y))
    if no >= 0:
      self.dragged_tab_id = self.tab_id(no)

  def on_dragging(self, event):
    if self.dragged_tab_id is None:
      return
    no = self.index(self.dragged_tab_id)
    no2 = self.index("@%d,%d" % (event.x, event.y))
    if no2 < 0 or no == no2:
      return
    tab_id = self.dragged_tab_id
    tab_id2 = self.tab_id(no)
    self.insert(no, self.tab_id_map_frame[tab_id])
    self.insert(no2, self.tab_id_map_frame[tab_id2])

  def on_drag_drop(self, event):
    self.dragged_tab_id = None

  @property
  def total(self):
    return self.index(tk.END)

  @property
  def curr(self):
    return self.index(tk.CURRENT)

  @property
  def sel_f(self):
    return self.tab_id_map_frame[self.select()]

  def idx(self, f):
    return self.frame_id_map_tab_id[id(f)]

  def del_tab(self, index=-1):
    if index < 0:
      if self.right_clicked_tab_id is not None:
        tab_id = self.right_clicked_tab_id
        self.right_clicked_tab_id = None
        index = self.index(tab_id)
      else:
        index = self.curr
        tab_id = self.tab_id(index)
    if len(self.tab_id_map_no) < 2: return
    self.forget(index)
    f = self.tab_id_map_frame[tab_id]
    del self.tab_id_map_frame[tab_id]
    del self.frame_id_map_tab_id[id(f)]
    bisect.insort(self.unused_no, self.tab_id_map_no[tab_id])
    del self.tab_id_map_no[tab_id]
    return tab_id

  def get_new_no(self):
    if len(self.unused_no):
      return self.unused_no.pop(0)
    else:
      return len(self.tab_id_map_no)

  def add_new_tab(self, f, pos=tk.END):
    no = self.get_new_no()
    if len(self.tabs()) == 0:
      self.add(f, text="New (%d)" % no)
    else:
      self.insert(pos, f, text="New (%d)" % no)
      self.select(pos if pos != tk.END else self.total - 1)
    self.frame_id_map_tab_id[id(f)] = self.select()
    self.tab_id_map_no[self.select()] = no
    self.tab_id_map_frame[self.select()] = f


class ClosableCustomNotebook(CustomNotebook):
  """A ttk Notebook with close buttons on each tab"""

  __initialized = False

  def __init__(self, *args, **kwargs):
    if not self.__initialized:
      self.__initialize_custom_style()
      self.__inititialized = True

    kwargs["style"] = "CustomNotebook"
    super().__init__(*args, **kwargs)

    self._active = None

    self.bind("<ButtonPress-1>", self.on_close_press, True)
    self.bind("<ButtonRelease-1>", self.on_close_release)

  def on_close_press(self, event):
    """Called when the button is pressed over the close button"""

    element = self.identify(event.x, event.y)

    if "close" in element:
      index = self.index("@%d,%d" % (event.x, event.y))
      self.state(['pressed'])
      self._active = index
      return "break"

  def on_close_release(self, event):
    """Called when the button is released"""
    if not self.instate(['pressed']):
      return

    element = self.identify(event.x, event.y)
    if "close" not in element:
      # user moved the mouse off of the close button
      return

    index = self.index("@%d,%d" % (event.x, event.y))

    if self._active == index:
      self.del_tab(index)
      self.event_generate("<<NotebookTabClosed>>")
      if len(self.id_map) == 0:
        self.add_new_tab()

    self.state(["!pressed"])
    self._active = None

  def __initialize_custom_style(self):
    style = ttk.Style()
    self.images = (
        tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
        tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
        tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
    )

    style.element_create("close", "image", "img_close",
                         ("active", "pressed", "!disabled", "img_closepressed"),
                         ("active", "!disabled", "img_closeactive"), border=8, sticky='')
    style.layout("CustomNotebook", [
                 ("CustomNotebook.client", {"sticky": "nswe"})])
    style.layout("CustomNotebook.Tab", [
        ("CustomNotebook.tab", {
            "sticky": "nswe",
            "children": [
                ("CustomNotebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("CustomNotebook.focus", {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [
                                ("CustomNotebook.label", {
                                 "side": "left", "sticky": ''}),
                                ("CustomNotebook.close", {
                                 "side": "left", "sticky": ''}),
                            ]
                        })
                    ]
                })
            ]
        })
    ])
