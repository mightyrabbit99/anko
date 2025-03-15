from core.parser import Parser
from core.generator import RdGenerator, Generator
from core.utils import Selector, Unit, Title, arr_to_csv_line, csv_line_to_arr
import pickle

def item_arr_render(x, delim=";", range_s=""):
  def trim_empty_tail(lst):
    while len(lst) > 0 and lst[-1] == "":
      lst.pop(-1)
    return lst
  sel = None
  try:
    sel = Selector(range_s)
  except:
    sel = None
  if sel:
    ans = [trim_empty_tail(sel.select(t, "")) for t in x]
    return [arr_to_csv_line(a, delim) if any(a) else str(x[i]) for i, a in enumerate(ans)][::-1]
  else:
    return [str(t) for t in x][::-1]

class Kernel:
  def __init__(self):
    self.his, self.hisi = [], -1
    self.delim = ";"
    self.generator = RdGenerator()

  def set_delim(self, delim):
    delim = delim.strip()
    if delim == "":
      return
    self.delim = delim

  @property
  def mode(self):
    return self.generator.typ

  def set_mode(self, mode):
    if mode == self.mode:
      return False
    gen = Generator
    if mode == 2:
      gen = RdGenerator
    self.generator = gen(self.generator.lst)
    self.reset()
    return True

  def reset(self):
    self.his, self.hisi = [], -1

  def read_wordlist_str(self, txt):
    self.reset()
    self.lst = Parser.parse_text(txt, self.delim).lst
    self.generator.set_lst(Unit("", self.lst).reverse(lambda x: len(x) > 0))

  def next(self, range_s=""):
    self.hisi += 1
    if self.hisi >= len(self.his):
      x = self.generator.next()
      self.his.append(x)
    return self.curr(range_s)

  def curr(self, range_s=""):
    if len(self.his) == 0:
      return self.next(range_s)
    x = self.his[self.hisi]
    return item_arr_render(x, self.delim, range_s)

  def edit_curr(self, lst, range_s=""):
    curr = self.his[self.hisi][::-1]
    sel = None
    try:
      sel = Selector(range_s)
    except:
      sel = None
    for i, ss in enumerate(lst[:len(curr)]):
      t = curr[i]
      if sel and any(sel.select(t, "")):
        sel.set_val_all(t, csv_line_to_arr(ss, self.delim))
      else:
        Title.set(t, ss)

  def prev(self, range_s=""):
    if not self.has_prev():
      raise Exception
    self.hisi -= 1
    return self.curr(range_s)

  def gen_text(self, range_s=""):
    sel = None
    try:
      sel = Selector(range_s)
    except Exception:
      sel = None
  
    def stringify(title):
      res = sel.select(title, "")
      if any(res):
        return arr_to_csv_line(res, self.delim)
      else:
        return str(title)
    if range_s != "" and sel is not None:
      lines = [x._str(stringify) for x in self.lst]
    else:
      lines = [str(x) for x in self.lst]
    return '\n'.join(lines)

  @property
  def count(self):
    return self.hisi

  def __len__(self):
    return len(self.generator)

  def has_prev(self):
    return len(self.his) > 0 and self.hisi > 0

  def is_empty(self):
    return self.generator.is_empty()

  def __str__(self):
    return pickle.dumps(self).decode('utf-8')
  
  @staticmethod
  def parse_from_bytes_str(s):
    return pickle.loads(bytes(s, 'utf-8'))
