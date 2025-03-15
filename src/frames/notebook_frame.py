import tkinter as tk
from stubs import TabController
from components import CustomNotebook as CNotebook

MAX_TAB_TITLE_LEN = 20

class NotebookFrame(CNotebook):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.default_generator = tk.Frame
    self.generators = {}
    self.render()

  def get_controller(self, scribble_frame):
    controller = TabController()
    index = self.idx(scribble_frame)

    def set_title(t):
      t = t.strip()
      if len(t) == 0:
        return
      if len(t) > MAX_TAB_TITLE_LEN:
        t = t[:MAX_TAB_TITLE_LEN] + "…"
      try:
        return self.tab(index, text=t)
      except:
        return None

    def get_title():
      try:
        return self.tab(index)['text']
      except:
        return None

    controller.set_title = set_title
    controller.get_title = get_title
    return controller

  def set_tab_generators(self, generators):
    for k in self.generators:
      self.tab_popup_menu.deletecommand("New %s" % k)
      self.popup_menu.deletecommand("New %s" % k)

    self.generators = dict(generators)
    self.default_generator = generators[0][1] if len(
        generators) > 0 else tk.Frame

    def add_new(k):
      return lambda: self.add_new_content_tab(k)

    for k in self.generators:
      self.tab_popup_menu.add_command(
          label="New %s" % k, command=add_new(k))
      self.popup_menu.add_command(
          label="New %s" % k, command=add_new(k))

  def add_new_content_tab(self, name=None):
    if name is None:
      F = self.default_generator
    else:
      F = self.generators[name]
    ans = F(self)
    if self.right_clicked_tab_id:
      self.add_new_tab(ans, self.index(self.right_clicked_tab_id))
    else:
      self.add_new_tab(ans)
    if hasattr(ans, "action_handler"):
      ans.action_handler.set_tab_controller(self.get_controller(ans))
    return ans

  def render(self):
    self.tab_popup_menu.add_separator()
    self.popup_menu = tk.Menu(self, tearoff=0)

  def popup(self, event):
    if super().popup(event):
      return True
    try:
      self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
      self.popup_menu.grab_release()
      return True

  def select_prev_tab(self):
    tab_id = self.select()
    index = self.index(tab_id)
    i = index - 1 if index > 0 else len(self.tabs()) - 1
    self.select(i)

  def select_next_tab(self):
    tab_id = self.select()
    index = self.index(tab_id)
    i = index + 1 if index + 1 < len(self.tabs()) else 0
    self.select(i)
