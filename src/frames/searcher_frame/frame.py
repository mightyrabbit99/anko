import tkinter as tk
from typing import Iterable
from components.txt_box import TxtBox

from stubs import ActionHandler, TabController, TabFrame
from .kernel import Kernel


class SearcherFrameController:
  def __init__(self, title_entry: tk.Entry, wordlist_panel: tk.Text, search_panel: tk.Text, disp_list: tk.Text):
    self.title_entry = title_entry
    self.wordlist_panel = wordlist_panel
    self.search_panel = search_panel
    self.disp_list = disp_list

  def settings(self):
    pass

  def clear_disp_list(self):
    self.disp_list.delete("1.0", tk.END)

  def set_disp_list(self, lst: Iterable[str]):
    self.disp_list.insert("1.0", '\n\n'.join(lst))

  def get_search_keyword(self):
    return self.search_panel.get("1.0", tk.END).strip()

  def highlight_search(self):
    self.search_panel.event_generate('<Control-a>')

  def clear_wordlist(self):
    self.wordlist_panel.delete("1.0", tk.END)

  def get_wordlist(self):
    return self.wordlist_panel.get("1.0", tk.END)

  def set_title(self, title):
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, title)

  def get_title(self):
    return self.title_entry.get()


class SearcherActionHandler(ActionHandler):
  def __init__(self):
    super().__init__()
    self.kernel = Kernel()
    self.frame_controller = None

  def set_frame_controller(self, controller: SearcherFrameController):
    self.frame_controller = controller
    controller.settings()

  def set_tab_controller(self, controller: TabController):
    self.tab_controller = controller
    self.frame_controller.set_title(controller.get_title())

  def search_button_click(self):
    if not self.kernel.has_lst():
      return
    keyword = self.frame_controller.get_search_keyword()
    res = self.kernel.get_closest(keyword, 5)
    self.frame_controller.clear_disp_list()
    self.frame_controller.set_disp_list(
        "{}\n  {}".format(
            a,
            '\n  '.join(
                '{}) {}'.format(i, '; '.join(c)) for i, c in enumerate(b, 1))
        ) for a, b in res
    )
    self.frame_controller.highlight_search()
    return 'break'

  def reload_button_click(self):
    self.kernel.load_lst(txt=self.frame_controller.get_wordlist())
    return 'break'

  def reset_title(self):
    if not self.tab_controller:
      return
    t = self.frame_controller.get_title().strip()
    if len(t) == 0:
      self.frame_controller.set_title(self.tab_controller.get_title())
    else:
      self.tab_controller.set_title(self.frame_controller.get_title())

  def shortcut_key_press_handler(self, e, key):
    if (key == '<F5>'):
      return self.reload_button_click()
    else:
      return None


style = {
    'title': {
        'w': 45,
    },
    'wordlist': {
        'h': 31,
        'w': 50,
    },
    # unit = character height/width
    'search_bar': {
        'h': 2,
        'w': 35,
    },
    'disp_list': {
        'h': 29,
        'w': 45,
    },
    'btn': {
        'h': 2,
        'w': 5,
    },
}


class SearcherFrame(TabFrame):
  def get_controller(self):
    return SearcherFrameController(self.title_entry, self.wordlist, self.search_box, self.disp_list)

  def __init__(self, window: tk.Frame):
    super().__init__(window)
    self.action_handler = SearcherActionHandler()
    self.render()
    self.action_handler.set_frame_controller(self.get_controller())

  def wordlist_panel(self, master):
    f = tk.Frame(master)
    title_entry = tk.Entry(
        f, width=style['title']['w'])
    title_entry.grid(row=0, column=0)
    title_entry.bind("<FocusOut>", lambda e: self.action_handler.reset_title())
    self.title_entry = title_entry
    f1, txt = TxtBox(f, width=style['wordlist']['w'],
                  height=style['wordlist']['h'], undo=True)
    f1.grid(row=1, column=0)
    txt.bind('<Shift-Return>', lambda e: self.action_handler.reload_button_click())
    self.wordlist = txt
    f.grid_rowconfigure(0, weight=3)
    f.grid_rowconfigure(1, weight=1)
    return f

  def interaction_panel(self, master):
    f = tk.Frame(master)

    def ctrl_buttons_panel(master):
      def gen_btn(master, text, onClick):
        return tk.Button(master, width=style['btn']['w'], height=style['btn']['h'],
                         text=text, command=onClick)
      f = tk.Frame(master)
      btn_lst = [
          ("Load", self.action_handler.reload_button_click),
          ("Search", self.action_handler.search_button_click),
      ]
      for name, func in btn_lst:
        btn = gen_btn(f, name, func)
        btn.pack(side=tk.LEFT)
      return f

    def search_box_panel(master):
      f = ctrl_buttons_panel(master)
      search_box = tk.Text(
          f, width=style['search_bar']['w'], height=style['search_bar']['h'], font=("Calibri", 12))
      search_box.bind(
          '<Return>', lambda e: self.action_handler.search_button_click())
      search_box.pack(side=tk.LEFT)

      return f, search_box

    def disp_list_panel(master):
      return TxtBox(
          master, width=style['disp_list']['w'], height=style['disp_list']['h'])

    f1, search_box = search_box_panel(f)
    f1.grid(row=0, column=0)
    self.search_box = search_box
    f2, disp_list = disp_list_panel(f)
    f2.grid(row=1, column=0)
    self.disp_list = disp_list

    f.grid_rowconfigure(0, weight=1)
    f.grid_rowconfigure(1, weight=2)
    return f

  def render(self):
    f = self
    wordlist_f = self.wordlist_panel(f)
    wordlist_f.grid(row=0, column=0)
    interaction_f = self.interaction_panel(f)
    interaction_f.grid(row=0, column=1)

    f.grid_columnconfigure(0, weight=2)
    f.grid_columnconfigure(1, weight=1)
    f.grid_rowconfigure(0, weight=1)
