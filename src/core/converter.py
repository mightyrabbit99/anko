import re

from core.utils import indent_forward
from .parser import Parser

def is_int_s(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


timestamp_expobj = re.compile(
    "[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} *--> *[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}")


def is_timestamp(s):
  """
    sample timestamp: 00:07:21,283 --> 00:07:23,750
  """
  return timestamp_expobj.match(s)


class Srt:
  class SrtUnit:
    def __init__(self, num=None, timestamp=None):
      self._num = num
      self._timestamp = timestamp
      self._contents = []

    def __str__(self):
      return "%s;%s\n\t%s" % (self._num, self._timestamp, self.get_content_str())

    @property
    def num(self):
      return self._num

    @property
    def timestamp(self):
      return self._timestamp

    @property
    def contents(self):
      return self._contents

    @num.setter
    def num(self, val):
      self._num = val

    @timestamp.setter
    def timestamp(self, val):
      self._timestamp = val

    def add_content(self, s):
      self._contents.append(s)

    def get_content_str(self):
      return " ".join(self._contents)

  def __init__(self, units=[]):
    self._units = units

  def __iter__(self):
    return iter(self._units)

  @staticmethod
  def parse(txt):
    lst = []
    curr = Srt.SrtUnit()

    def read_line(l):
      nonlocal lst, curr
      if is_int_s(l):
        lst.append(curr)
        curr = Srt.SrtUnit(l)
      elif is_timestamp(l):
        curr.timestamp = l
      else:
        if curr.timestamp is None:
          raise Exception("srt file format not observed!")
        curr.add_content(l)
    for l in txt.split("\n"):
      l = l.strip()
      if len(l) == 0:
        continue
      read_line(l)
    lst.append(curr)
    return Srt(lst[1:])


def srt_to_indented_txt(srt):
  return "\n".join(str(u) for u in srt)


def srt_txt_to_indented_txt(s):
  s = s.strip()
  return srt_to_indented_txt(Srt.parse(s))

def srt_txt_to_paragraphs_txt(s):
  s = s.strip()
  return " ".join(x.get_content_str() for x in Srt.parse(s))

intersentence_expobj = re.compile("(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")
def paragraphs_txt_to_indented_txt(s: str):
  s = s.strip()
  lst = intersentence_expobj.split(s)
  return "\n".join(lst)

def indented_txt_to_layered_txt(s: str):
  s = s.strip()
  if len(s) == 0: return ""
  u = Parser.parse_text(s, None)
  layers = u.stratumise()
  lst = ["1\n%s" % indent_forward("\n".join(layers[0].get_raw_subtitles()))]
  for i, layer in enumerate(layers[1:]):
    content = layer.str_entries_with_sub()
    if len(content) == 0:
      break
    lst.append("1%s\n%s" % (":1" * (i + 1), indent_forward(content)))
  return "\n".join(lst)
