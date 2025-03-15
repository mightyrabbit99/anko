import tkinter as tk
import tkinter.ttk as ttk
from stubs import ActionHandler, TabController, TabFrame
from components import TxtBox, Entry1
from .kernel import Kernel


class AnkiFrameController:
  def __init__(self, title_entry: tk.Entry, wordlist_panel: tk.Text,
               disp_panel1: tk.Text,
               disp_panel2: tk.Text,
               num_entry1: tk.Entry,
               num_entry2: tk.Entry,
               prog_bar: ttk.Progressbar,
               prog_lbl: tk.StringVar):
    self.title_entry = title_entry
    self.wordlist_panel = wordlist_panel
    self.disp_panel1 = disp_panel1
    self.disp_panel2 = disp_panel2
    self.num_entry1 = num_entry1
    self.num_entry2 = num_entry2
    self.prog_bar = prog_bar
    self.prog_lbl = prog_lbl

  def settings(self):
    self.disp_panel1.config(state=tk.DISABLED)

  def get_title(self):
    return self.title_entry.get()

  def get_wordlist(self):
    return self.wordlist_panel.get("1.0", tk.END)

  def get_text2(self):
    return self.disp_panel2.get("1.0", tk.END)

  def get_num1(self):
    return self.num_entry1.get()

  def get_num2(self):
    return self.num_entry2.get()

  def clear_text1(self):
    self.disp_panel1.delete("1.0", tk.END)

  def clear_then_show_text1(self, txt):
    self.disp_panel1.config(state=tk.NORMAL)
    self.disp_panel1.replace("1.0", tk.END, txt)
    self.disp_panel1.config(state=tk.DISABLED)

  def clear_text2(self):
    self.disp_panel2.delete("1.0", tk.END)
    self.disp_panel2.edit_reset()
    self.disp_panel2.config(state=tk.DISABLED)

  def clear_then_show_text2(self, txt):
    self.disp_panel2.config(state=tk.NORMAL)
    self.disp_panel2.replace("1.0", tk.END, txt)
    self.disp_panel2.edit_reset()

  def clear_wordlist(self):
    self.wordlist_panel.delete("1.0", tk.END)

  def set_wordlist(self, txt):
    self.wordlist_panel.replace("1.0", tk.END, txt)

  def set_progress(self, curr, total):
    c = curr % total + 1
    self.prog_bar['value'] = c / total * 100
    self.prog_lbl.set('%d/%d' % (c, total))

  def set_title(self, title):
    if title == self.get_title():
      return
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, title)
    self.title_entry.event_generate("<FocusOut>", when="tail")


class AnkiActionHandler(ActionHandler):
  def __init__(self):
    super().__init__()
    self.kernel = Kernel()
    self.frame_controller = None
    self.show_pressed = False

  def set_frame_controller(self, controller: AnkiFrameController):
    self.frame_controller = controller
    controller.settings()

  def set_tab_controller(self, controller: TabController):
    self.tab_controller = controller
    self.frame_controller.set_title(controller.get_title())

  def show_text1(self):
    self.text1_num = self.frame_controller.get_num1()
    self.frame_controller.clear_then_show_text1(
        "\n".join(self.kernel.curr(self.text1_num)))

  def show_text2(self):
    self.text2_num = self.frame_controller.get_num2()
    self.frame_controller.clear_then_show_text2(
        "\n".join(self.kernel.curr(self.text2_num)))

  def save_button_click(self):
    if not self.show_pressed:
      return
    s = self.frame_controller.get_text2()
    if not s or self.kernel.curr() == s:
      return
    num2 = self.frame_controller.get_num2()
    if self.text2_num != num2:
      return
    lst = [x.strip() for x in s.split('\n')]
    self.kernel.edit_curr(lst, num2)

  def next_button_click(self):
    if self.kernel.is_empty():
      return
    self.save_button_click()
    self.kernel.next()
    self.show_text1()
    self.frame_controller.clear_text2()
    self.frame_controller.set_progress(
        self.kernel.item_count, len(self.kernel))
    self.show_pressed = False

  def prev_button_click(self):
    if self.kernel.has_prev():
      self.save_button_click()
      self.kernel.prev()
      self.show_text1()
      self.frame_controller.clear_text2()
      self.frame_controller.set_progress(
          self.kernel.item_count, len(self.kernel))
      self.show_pressed = False

  def reload_button_click(self):
    self.kernel.read_wordlist_str(txt=self.frame_controller.get_wordlist())
    self.show_pressed = False
    self.next_button_click()

  def render_button_click(self):
    if self.kernel.is_empty():
      return
    if self.show_pressed:
      self.save_button_click()
    self.frame_controller.set_wordlist(self.kernel.gen_text())

  def show_button_click(self):
    if self.kernel.is_empty():
      return
    self.show_text2()
    self.show_pressed = True

  def set_tab_title(self, t=None):
    if not self.tab_controller:
      return
    if t is None:
      t = self.frame_controller.get_title().strip()
    t_old = self.tab_controller.get_title().strip()
    if t != t_old:
      self.tab_controller.set_title(t)

  def reset_title(self):
    if not self.tab_controller:
      return
    t = self.frame_controller.get_title().strip()
    if len(t) == 0:
      self.frame_controller.set_title(self.tab_controller.get_title())
    else:
      self.set_tab_title(t)

  def set_mode(self, md):
    if not self.kernel.set_mode(md):
      return
    self.show_pressed = False
    self.next_button_click()

  def refresh_text1(self):
    if self.kernel.is_empty():
      return
    self.show_text1()

  def refresh_text2(self):
    if not self.show_pressed or self.kernel.is_empty():
      return
    self.show_text2()

  def shortcut_key_press_handler(self, e, key):
    if (key == '<F2>'):
      return self.prev_button_click()
    elif (key == '<F3>'):
      return self.show_button_click()
    elif (key == '<F4>'):
      return self.next_button_click()
    elif (key == '<F5>'):
      return self.reload_button_click()
    elif (key == '<F6>'):
      return self.render_button_click()
    elif (key == '<Control-s>'):
      return self.render_button_click()
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
    'prog_bar': {
        'w': 285,
    },
    'prog_label': {
        'w': 10,
    },
    'disp': {
        'h': 11,
        'w': 45,
    },
    'btn': {
        'h': 2,
        'w': 5,
    },
    'num1': {
        'h': 2,
        'w': 10,
    },
}


class AnkiFrame(TabFrame):
  def get_controller(self):
    return AnkiFrameController(
        self.title_entry,
        self.wordlist,
        self.disp1,
        self.disp2,
        self.num_entry1,
        self.num_entry2,
        self.prog_bar,
        self.prog_lbl)

  def __init__(self, window: tk.Frame):
    super().__init__(window)
    self.action_handler = AnkiActionHandler()
    self.render()
    self.action_handler.set_frame_controller(self.get_controller())

  def wordlist_panel(self, master):
    f = tk.Frame(master)
    title_entry = Entry1(
        f, width=style['title']['w'])
    title_entry.grid(row=0, column=0)
    title_entry.bind("<Return>", lambda e: self.action_handler.set_tab_title())
    title_entry.bind("<FocusOut>", lambda e: self.action_handler.reset_title())
    self.title_entry = title_entry

    ff2, txt = TxtBox(f, width=style['wordlist']['w'],
                      height=style['wordlist']['h'], undo=True)
    ff2.grid(row=1, column=0)
    self.wordlist = txt

    f.grid_rowconfigure(0, weight=3)
    f.grid_rowconfigure(1, weight=1)

    return f

  def interaction_panel(self, master):
    f = tk.Frame(master)

    def prog_bar(master):
      f = tk.Frame(master)

      v = tk.StringVar()
      lbl = tk.Label(f, textvariable=v, relief=tk.SUNKEN,
                     width=style['prog_label']['w'])
      lbl.pack(side=tk.LEFT, padx=2, pady=2)
      prog = ttk.Progressbar(f, orient=tk.HORIZONTAL,
                             length=style['prog_bar']['w'], mode='determinate')
      prog.pack(side=tk.LEFT, padx=2, pady=2)

      return f, prog, v

    def disp_panel(master):
      f = tk.Frame(master)
      ff1, txt1 = TxtBox(f, width=style['disp']['w'],
                         height=style['disp']['h'], font=("Calibri", 12))
      ff1.grid(row=0, column=0)
      ff2, txt2 = TxtBox(f, width=style['disp']['w'],
                         height=style['disp']['h'], font=("Calibri", 12), undo=True)
      ff2.grid(row=1, column=0)
      return f, txt1, txt2

    def ctrl_panel(master):
      def button_panel(master):
        def gen_btn(master, text, onClick):
          return tk.Button(master, width=style['btn']['w'], height=style['btn']['h'],
                           text=text, command=onClick)
        f = tk.Frame(master)
        btn_lst = [
            ("Load", self.action_handler.reload_button_click),
            ("Rend", self.action_handler.render_button_click),
            ("Prev", self.action_handler.prev_button_click),
            ("Show", self.action_handler.show_button_click),
            ("Next", self.action_handler.next_button_click),
        ]
        btns = []
        for name, func in btn_lst:
          btn = gen_btn(f, name, func)
          btn.pack(side=tk.LEFT, padx=1, pady=1)
          btns.append(btn)

        def gen_label(master, text):
          lbl_f = tk.Frame(master)
          lbl1 = tk.Label(lbl_f, text=text)
          lbl1.pack(side=tk.LEFT)
          num_entry = Entry1(
              lbl_f, width=style['num1']['w'])
          num_entry.pack(side=tk.LEFT)
          return lbl_f, num_entry

        lbls = tk.Frame(f)
        lbl_f1, self.num_entry1 = gen_label(lbls, "idx1:")
        lbl_f2, self.num_entry2 = gen_label(lbls, "idx2:")
        self.num_entry1.bind(
            "<Return>", lambda e: self.action_handler.refresh_text1())
        self.num_entry1.bind(
            "<FocusOut>", lambda e: self.action_handler.refresh_text1())
        self.num_entry2.bind(
            "<Return>", lambda e: self.action_handler.refresh_text2())
        self.num_entry2.bind(
            "<FocusOut>", lambda e: self.action_handler.refresh_text2())
        lbl_f1.pack(side=tk.TOP)
        lbl_f2.pack(side=tk.TOP)
        lbls.pack(side=tk.LEFT, padx=2, pady=2)
        return f, btns

      def mode_panel(master):
        f = tk.Frame(master)
        mode_var = tk.IntVar(f, 2)
        md_lst = [
            ("Normal", lambda: self.action_handler.set_mode(1)),
            ("Random", lambda: self.action_handler.set_mode(2)),
        ]
        radios = []
        for i, (name, func) in enumerate(md_lst, 1):
          r = tk.Radiobutton(f, text=name, variable=mode_var,
                             value=i, command=func)
          r.pack(side=tk.LEFT)
          radios.append(r)
        return f, mode_var, radios

      f = tk.Frame(master)
      btn_f, btns = button_panel(f)
      btn_f.pack(side=tk.TOP)
      mode_f, self.mode_var, radios = mode_panel(f)
      mode_f.pack(side=tk.TOP)
      return f

    # prevent variables from being garbage collected
    prog, self.prog_bar, self.prog_lbl = prog_bar(f)
    prog.grid(row=0, column=0)
    disp, self.disp1, self.disp2 = disp_panel(f)
    disp.grid(row=1, column=0)
    ctrl = ctrl_panel(f)
    ctrl.grid(row=2, column=0)

    f.grid_rowconfigure(0, weight=3)
    f.grid_rowconfigure(1, weight=1)
    f.grid_rowconfigure(2, weight=1)
    return f

  def render(self):
    f = self
    wordlist_f = self.wordlist_panel(f)
    wordlist_f.grid(row=0, column=0)
    interaction_f = self.interaction_panel(f)
    interaction_f.grid(row=0, column=1)

    f.grid_columnconfigure(0, weight=1)
    f.grid_columnconfigure(1, weight=0)
    f.grid_rowconfigure(0, weight=1)
