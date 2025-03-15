import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from utils.tk import text_sel_all
from stubs import ActionHandler, TabController, TabFrame
from components import TxtBox, Entry1
from .kernel import Kernel
from core.converter import indented_txt_to_layered_txt, srt_txt_to_indented_txt, paragraphs_txt_to_indented_txt, srt_txt_to_paragraphs_txt


class PrompterFrameController:
  def __init__(self, elements):
    self.title_entry = elements['title_entry']
    self.delim_entry = elements['delim_entry']
    self.wordlist_panel = elements['wordlist_panel']
    self.disp_panel1 = elements['disp_panel1']
    self.disp_panel2 = elements['disp_panel2']
    self.num_entry1 = elements['num_entry1']
    self.num_entry2 = elements['num_entry2']
    self.prog_bar = elements['prog_bar']
    self.prog_lbl = elements['prog_lbl']
    self.round_lbl = elements['round_lbl']

  def settings(self):
    # self.disp_panel1.config(state=tk.DISABLED)
    pass

  def get_title(self):
    return self.title_entry.get()

  def get_delim(self):
    return self.delim_entry.get()

  def get_wordlist(self):
    return self.wordlist_panel.get("1.0", tk.END)

  def get_text2(self):
    return self.disp_panel2.get("1.0", tk.END)

  def get_num1(self):
    return self.num_entry1.get()

  def get_num2(self):
    return self.num_entry2.get()

  def clear_text1(self):
    origin_state = self.disp_panel2['state']
    self.disp_panel1.config(state=tk.NORMAL)
    self.disp_panel1.delete("1.0", tk.END)
    self.disp_panel1.config(state=origin_state)

  def clear_then_show_text1(self, txt):
    origin_state = self.disp_panel2['state']
    self.clear_text1()
    self.disp_panel1.config(state=tk.NORMAL)
    self.disp_panel1.replace("1.0", tk.END, txt)
    self.disp_panel1.config(state=origin_state)

  def clear_text2(self):
    origin_state = self.disp_panel2['state']
    self.disp_panel2.config(state=tk.NORMAL)
    self.disp_panel2.delete("1.0", tk.END)
    self.disp_panel2.edit_reset()  # reset edit history
    self.disp_panel2.config(state=origin_state)

  def clear_then_show_text2(self, txt):
    origin_state = self.disp_panel2['state']
    self.clear_text2()
    self.disp_panel2.config(state=tk.NORMAL)
    self.disp_panel2.replace("1.0", tk.END, txt)
    self.disp_panel2.edit_reset()
    self.disp_panel2.config(state=origin_state)

  def clear_wordlist(self):
    self.wordlist_panel.delete("1.0", tk.END)

  def set_wordlist(self, txt):
    self.wordlist_panel.replace("1.0", tk.END, txt)

  def set_progress(self, curr, total):
    d, r = int(curr / total), curr % total + 1
    self.prog_bar['value'] = r / total * 100
    self.prog_lbl.set('%d/%d' % (r, total))
    self.round_lbl.set(str(d))

  def set_title(self, title):
    if title == self.get_title():
      return
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, title)
    self.title_entry.event_generate("<FocusOut>", when="tail")

  def set_delim(self, delim):
    if delim == self.get_delim():
      return
    self.delim_entry.delete(0, tk.END)
    self.delim_entry.insert(0, delim)
    self.delim_entry.event_generate("<FocusOut>", when="tail")


class PrompterActionHandler(ActionHandler):
  def __init__(self):
    super().__init__()
    self.kernel = Kernel()
    self.frame_controller = None
    self.show_pressed = False

  def set_frame_controller(self, controller: PrompterFrameController):
    self.frame_controller = controller
    self.frame_controller.set_delim(self.kernel.delim)
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
    self.frame_controller.set_progress(self.kernel.count, len(self.kernel))
    self.show_pressed = False

  def prev_button_click(self):
    if self.kernel.has_prev():
      self.save_button_click()
      self.kernel.prev()
      self.show_text1()
      self.frame_controller.clear_text2()
      self.frame_controller.set_progress(self.kernel.count, len(self.kernel))
      self.show_pressed = False

  def reload_button_click(self):
    s = self.frame_controller.get_wordlist()
    if s.strip() == "":
      return
    self.reset_delim()
    self.kernel.read_wordlist_str(txt=s)
    self.show_pressed = False
    self.next_button_click()

  def render_button_click(self):
    self.reset_delim()
    if self.kernel.is_empty():
      return
    if self.show_pressed:
      self.save_button_click()
    self.frame_controller.set_wordlist(self.kernel.gen_text(self.frame_controller.get_num2()))

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

  def set_delim(self, t=None):
    if t is None:
      t = self.frame_controller.get_delim().strip()
    delim_old = self.kernel.delim
    if t != delim_old:
      self.kernel.set_delim(t)

  def reset_delim(self):
    t = self.frame_controller.get_delim().strip()
    if len(t) == 0:
      self.frame_controller.set_delim(self.kernel.delim)
    else:
      self.set_delim(t)

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

  def conv_srt_to_indented_txt(self):
    s = self.frame_controller.get_wordlist()
    self.frame_controller.set_wordlist(srt_txt_to_indented_txt(s))


style = {
    'title': {
        'w': 45,
    },
    'delim': {
        'w': 2,
    },
    'wordlist': {
        'h': 31,
        'w': 50,
    },
    'prog_bar': {
        'w': 285,
    },
    'rounds_label': {
        'w': 2,
    },
    'prog_label': {
        'w': 8,
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


class PrompterFrame(TabFrame):
  def get_controller(self):
    elements = {
        "title_entry": self.title_entry,
        "delim_entry": self.delim_entry,
        "wordlist_panel": self.wordlist,
        "disp_panel1": self.disp1,
        "disp_panel2": self.disp2,
        "num_entry1": self.num_entry1,
        "num_entry2": self.num_entry2,
        "prog_bar": self.prog_bar,
        "prog_lbl": self.prog_lbl,
        "round_lbl": self.round_lbl,
    }
    return PrompterFrameController(elements)

  def __init__(self, window: tk.Frame):
    super().__init__(window)
    self.action_handler = PrompterActionHandler()
    self.render()
    self._install_popups()
    self.action_handler.set_frame_controller(self.get_controller())

  def _install_wordlist_popups(self):
    txt = self.wordlist
  
    def conv_f(f):
      s = txt.get("1.0", tk.END)
      try:
        txt.replace("1.0", tk.END, f(s))
      except Exception as e:
        messagebox.showerror("Error", e)

    popup_menu = tk.Menu(txt, tearoff=0)
    popup_menu.add_command(label="Select all", command=lambda : text_sel_all(txt))
    convert_menu = tk.Menu(popup_menu, tearoff=0)
    convert_menu.add_command(
        label="srt->ind_txt", command=lambda: conv_f(srt_txt_to_indented_txt))
    convert_menu.add_command(
        label="srt->para", command=lambda: conv_f(srt_txt_to_paragraphs_txt))
    convert_menu.add_command(
        label="para->ind_txt", command=lambda: conv_f(paragraphs_txt_to_indented_txt))
    convert_menu.add_command(label="ind_txt->lyrd_txt",
                             command=lambda: conv_f(indented_txt_to_layered_txt))
    popup_menu.add_cascade(label="Convert", menu=convert_menu)

    def popup(event):
      popup_menu.tk_popup(event.x_root, event.y_root, 0)
    txt.bind("<Button-3>", popup)

  def _install_popups(self):
    self._install_wordlist_popups()

  def wordlist_panel(self, master):
    f = tk.Frame(master)

    def metadata_panel(master):
      f = tk.Frame(master)

      def metadata_unit(master, name, input_width):
        f = tk.Frame(master)
        lbl1 = tk.Label(f, text="%s:" % name)
        lbl1.pack(side=tk.LEFT)
        title_entry = Entry1(f, width=input_width)
        title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        return f, title_entry
      ff1, title_entry = metadata_unit(f, "Title", style['title']['w'])
      title_entry.bind(
          "<Return>", lambda e: self.action_handler.set_tab_title())
      title_entry.bind(
          "<FocusOut>", lambda e: self.action_handler.reset_title())
      self.title_entry = title_entry
      ff1.pack(side=tk.LEFT, fill=tk.X, expand=True)
      ff2, delim_entry = metadata_unit(f, "Delim", style['delim']['w'])
      delim_entry.bind(
          "<Return>", lambda e: self.action_handler.set_delim())
      delim_entry.bind(
          "<FocusOut>", lambda e: self.action_handler.reset_delim())
      self.delim_entry = delim_entry
      ff2.pack(side=tk.RIGHT)

      return f

    ff1 = metadata_panel(f)
    ff1.grid(row=0, column=0, sticky="ew")
    ff2, txt = TxtBox(f, width=style['wordlist']['w'],
                      height=style['wordlist']['h'], undo=True)
    ff2.grid(row=1, column=0, sticky="nsew")
    self.wordlist = txt

    f.grid_rowconfigure(0, weight=0)
    f.grid_rowconfigure(1, weight=1)
    f.grid_columnconfigure(0, weight=1)

    return f

  def interaction_panel(self, master):
    f = tk.Frame(master)

    def prog_bar(master):
      f = tk.Frame(master)

      v1 = tk.StringVar()
      lbl = tk.Label(f, textvariable=v1, relief=tk.SUNKEN,
                     width=style['rounds_label']['w'])
      lbl.pack(side=tk.LEFT, padx=1)
      v2 = tk.StringVar()
      lbl2 = tk.Label(f, textvariable=v2, relief=tk.SUNKEN,
                     width=style['prog_label']['w'])
      lbl2.pack(side=tk.LEFT, padx=1)
      prog = ttk.Progressbar(f, orient=tk.HORIZONTAL,
                             length=style['prog_bar']['w'], mode='determinate')
      prog.pack(side=tk.LEFT, padx=2, pady=1, fill=tk.X, expand=True)

      return f, prog, v1, v2

    def disp_panel(master):
      f = tk.Frame(master)
      ff1, txt1 = TxtBox(f, width=style['disp']['w'],
                         height=style['disp']['h'], wrap=tk.WORD, font=("Calibri", 12))
      ff1.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew")
      ff2, txt2 = TxtBox(f, width=style['disp']['w'],
                         height=style['disp']['h'], wrap=tk.WORD, font=("Calibri", 12), undo=True)
      ff2.grid(row=1, column=0, rowspan=1, columnspan=1, sticky="nsew")
      f.grid_rowconfigure(0, weight=1)
      f.grid_rowconfigure(1, weight=1)
      f.grid_columnconfigure(0, weight=1)
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
    prog, self.prog_bar, self.round_lbl, self.prog_lbl = prog_bar(f)
    prog.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="ew")
    disp, self.disp1, self.disp2 = disp_panel(f)
    disp.grid(row=1, column=0, columnspan=1, rowspan=1, sticky="nsew")
    ctrl = ctrl_panel(f)
    ctrl.grid(row=2, column=0, columnspan=1, rowspan=1, sticky="ew")

    f.grid_rowconfigure(0, weight=0)
    f.grid_rowconfigure(1, weight=1)
    f.grid_rowconfigure(2, weight=0)
    f.grid_columnconfigure(0, weight=1)
    return f

  def render(self):
    f = self
    wordlist_f = self.wordlist_panel(f)
    wordlist_f.grid(row=0, column=0, columnspan=1, sticky="nsew")
    interaction_f = self.interaction_panel(f)
    interaction_f.grid(row=0, column=1, columnspan=1, sticky="nsew")
    

    f.grid_columnconfigure(0, weight=8)
    f.grid_columnconfigure(1, weight=1)
    f.grid_rowconfigure(0, weight=1)
