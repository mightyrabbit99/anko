import tkinter as tk

from utils.tk import text_copy_sel, text_sel_all


def Entry1(*args, **kwargs):
  def select_all(widget):
    # select text
    widget.select_range(0, 'end')
    # move cursor to the end
    widget.icursor('end')
  ans = tk.Entry(*args, **kwargs)
  ans.bind('<Control-a>', lambda e: select_all(ans))
  return ans


class CustomText(tk.Text):
  def __init__(self, *args, **kwargs):
    """A text widget that report on internal widget commands"""
    tk.Text.__init__(self, *args, **kwargs)

    # switch to avoid infinite recursion
    self.proxy_switch = True

    # create a proxy for the underlying widget
    self._orig = self._w + "_orig"
    self.tk.call("rename", self._w, self._orig)
    self.tk.createcommand(self._w, self._proxy)

  def _proxy(self, command, *args):
    cmd = (self._orig, command) + args
    try:
      result = self.tk.call(cmd)
    except:
      return

    if command in ("insert", "delete", "replace") and self.proxy_switch:
      self.event_generate("<<TextModified>>")

    if (command in ("insert", "delete") or (command, *args[1:3]) == ("mark", "set", "insert")) and self.proxy_switch:
      self.event_generate("<<CursorChange>>", when="tail")

    return result


def TxtBox(master, *args, **kwargs):
  f = tk.Frame(master)

  sb = tk.Scrollbar(f)
  sb.pack(side=tk.RIGHT, fill=tk.Y)

  txt = CustomText(f, yscrollcommand=sb.set, *args, **kwargs)
  # scrollbar corresponds to y-axis of text
  sb.config(command=txt.yview)

  def line_no(pos):
    return int(pos.split('.')[0])

  # line background color
  txt.tag_configure("even", background="#e0e0e0", foreground="#000000")
  txt.tag_configure("odd", background="#ffffff", foreground="#000000")
  # txt.tag_configure(tk.SEL, background="#0078d7", foreground="#ffffff")
  txt.tag_lower("even")  # tk.SEL prevails
  txt.tag_lower("odd")  # tk.SEL prevails
  def tag_content(event):
    end_no = line_no(txt.index(tk.END))  # tk.INSERT = cursor pos
    txt.tag_remove("even", "1.0", tk.END)
    txt.tag_remove("odd", "1.0", tk.END)
    tag = "odd"
    for i in range(1, end_no):
      txt.tag_add(tag, "%d.0" % i, "%d.0" % (i + 1))
      tag = "even" if tag == "odd" else "odd"

  txt.bind("<<TextModified>>", tag_content)
  # copy highlighted text shortcut
  txt.bind('<Control-c>', lambda e: text_copy_sel(txt))
  txt.bind('<Control-a>', lambda e: text_sel_all(txt))

  '''
  # zoom in/out on mousescroll
  def zoom(event):
    print(txt["width"])
    font = txt["font"].split(" ")
    if len(font) < 2:
      return
    sgn = 1 if event.delta > 0 else -1
    txt.config(width=int(txt["width"] * math.pow(1.2, sgn)), height=int(txt["height"]
               * math.pow(1.2, sgn)), font=(font[0], int(font[1]) + 5 * sgn))
    # print(event.delta)
  txt.bind("<Control-MouseWheel>", zoom)
  '''
  txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
  return f, txt
