from typing import List
import io
import numpy as np
import pandas as pd


class Selector:
  def __init__(self, range_txt):
    self.s = range_txt
    self.low_unbounded, self.top_unbounded = False, False
    rgs = [x.strip() for x in range_txt.split(',')]
    if any(not x for x in rgs):
      raise ValueError
    if rgs[0][0] == '-':
      self.low_unbounded, self.low_i = True, int(rgs[0][1:])
      rgs.pop(0)
    if len(rgs) > 0 and rgs[-1][-1] == '-':
      self.top_unbounded, self.top_i = True, int(rgs[-1][:-1])
      rgs.pop(-1)

    self.i_lst = []
    if self.low_unbounded:
      self.i_lst.extend(range(0, self.low_i + 1))
    for rg in rgs:
      ab = rg.split('-')
      if len(ab) == 1:
        self.i_lst.extend(range(int(ab[0]), int(ab[0]) + 1))
      elif len(ab) == 2:
        self.i_lst.extend(range(int(ab[0]), int(ab[1]) + 1))
      else:
        raise ValueError

  def __contains__(self, i):
    if self.top_unbounded and i >= self.top_i:
      return True
    return i in self.i_lst

  def __getitem__(self, idx):
    def f(i):
      if i >= len(self.i_lst):
        if self.top_unbounded:
          return self.top_i + i - len(self.i_lst)
        else:
          raise IndexError
      return self.i_lst[i]
    if isinstance(idx, int):
      return f(idx)
    elif isinstance(idx, slice):
      if idx.stop is None and self.top_unbounded:
        raise ValueError
      return [f(i) for i in range(
          0 if idx.start is None else idx.start,
          min(len(self), len(self) if idx.stop is None else idx.stop),
          1 if idx.step is None else idx.step)]

  def __delitem__(self, idx):
    if idx >= len(self.i_lst):
      if self.top_unbounded:
        new_top_i = self[idx]
        self.i_lst.extend(range(self.top_i, new_top_i))
        return self.top_i + self.it_i - len(self.i_lst)
      else:
        raise IndexError
    self.i_lst.pop(idx)

  def __str__(self):
    return self.s

  class Iterator:
    def __init__(self, i_lst, top_i=None):
      self.i_lst = i_lst
      self.it_i = 0
      self.top_unbounded = top_i is not None
      self.top_i = top_i

    def __next__(self):
      if self.it_i >= len(self.i_lst):
        if self.top_unbounded:
          return self.top_i + self.it_i - len(self.i_lst)
        else:
          raise StopIteration
      else:
        return self.i_lst[self.it_i]

  def __iter__(self):
    return self.Iterator(self.i_lst, self.top_i if self.top_unbounded else None)

  def select(self, lst, default_value=None):
    def f(i):
      try:
        return lst[i]
      except Exception as e:
        if default_value is not None:
          return default_value
        else:
          raise IndexError
    ans = [f(i) for i in self.i_lst]
    if self.top_unbounded:
      ans.extend(lst[self.top_i:])
    return ans

  def set_val(self, lst, vals):
    for idx, v in enumerate(vals):
      try:
        pos = self[idx]
      except:
        break
      lst[pos] = v

  def set_val_all(self, lst, vals):
    for idx, v in enumerate(vals):
      try:
        pos = self[idx]
      except:
        break
      try:
        lst[pos] = v
      except:
        continue


def when_failed(default_val):
  def decorator(f):
    def ff(*args, **kwargs):
      try:
        return f(*args, **kwargs)
      except:
        return default_val
    return ff
  return decorator


@when_failed([])
def parse_range(s):
  def parse_range2(x):
    if '-' in x:
      lst = [x.strip() for x in x.split('-') if x.strip()]
      if len(lst) != 2:
        raise Exception
      return [*range(int(lst[0]), int(lst[1]) + 1)]
    else:
      return [int(x)]
  lst = [x.strip() for x in s.split(',') if x.strip()]
  if len(lst) == 0:
    return set()
  ans = []
  for r in map(parse_range2, lst):
    ans.extend(r)
  return ans


def stripf(*args):
  def stripff(f):
    def fff(*args2, **kwargs2):
      return f(*args2, **kwargs2).strip(*args)
    return fff
  return stripff


def levenshtein_ratio_and_distance(s, t, ratio_calc=True):
  """ 
    levenshtein_ratio_and_distance:
    Calculates levenshtein distance between two strings.
    If ratio_calc = True, the function computes the
    levenshtein distance ratio of similarity between two strings
    For all i and j, distance[i,j] will contain the Levenshtein
    distance between the first i characters of s and the
    first j characters of t
  """
  # Initialize matrix of zeros
  rows = len(s) + 1
  cols = len(t) + 1
  distance = np.zeros((rows, cols), dtype=int)

  # Populate matrix of zeros with the indeces of each character of both strings
  for i in range(1, rows):
    for k in range(1, cols):
      distance[i][0] = i
      distance[0][k] = k

  # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
  for col in range(1, cols):
    for row in range(1, rows):
      # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
      # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
      # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
      cost = 0 if s[row-1] == t[col-1] else 2 if ratio_calc else 1
      distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                               # Cost of insertions
                               distance[row][col-1] + 1,
                               distance[row-1][col-1] + cost)     # Cost of substitutions
  ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
  return ratio if ratio_calc else distance[row][col]


def max_elem(lst, N, f=lambda x: x):
  lst2 = [*lst]
  if N >= len(lst2):
    return lst2
  ans = []
  for _ in range(N):
    m = max(lst2, key=f)
    ans.append(m)
    lst2.remove(m)
  return ans


def indent_forward(s: str, n=1):
  return "\n".join("%s%s" % ("\t"*n, x) for x in s.split("\n"))


def indent_backward(s: str, n=1):
  def trim_indent(l: str, n=1):
    mx_n = l.find(l.strip())
    return l[min(mx_n, n):]
  return "\n".join(trim_indent(x, n) for x in s.split("\n"))


delim = ";"


def csv_line_to_arr(s: str, delim=None):
  def parse_cell(x):
    if type(x) == str:
      return x.strip()
    elif type(x) == np.int64:
      return str(x)
    else:
      return ""
  if '"' not in s and "'" not in s:
    return [s] if delim is None else s.split(delim)
  else:
    return [parse_cell(x) for x in pd.read_csv(io.StringIO(s), delimiter=delim, header=None).iloc[0]]


def arr_to_csv_line(arr, delim=delim):
  if len(arr) == 0: return ""
  if delim is None:
    return arr[0]
  if all(delim not in x for x in arr):
    return delim.join(arr)
  else:
    with io.StringIO() as sio:
      pd.DataFrame([arr]).to_csv(sio, sep=delim, header=None, index=False)
      sio.seek(0)
      return sio.read()[:-2]


class Title:
  def __init__(self, lst=None, delim=delim):
    self.lst = [] if lst is None else lst
    self.delim = delim
    self.ti = arr_to_csv_line(self.lst, self.delim)

  @stripf()
  def __str__(self):
    return self.ti

  def __len__(self):
    return len(self.lst)

  def __getitem__(self, idx):
    if isinstance(idx, int):
      return self.lst[idx]
    elif isinstance(idx, slice):
      return [self.lst[i] for i in range(
          0 if idx.start is None else idx.start,
          min(len(self.lst), len(self.lst) if idx.stop is None else idx.stop),
          1 if idx.step is None else idx.step)]

  def __setitem__(self, idx, item):
    self.lst[idx] = item
    self.ti = arr_to_csv_line(self.lst, self.delim)

  def __contains__(self, i):
    if not isinstance(i, int):
      return False
    return i < len(self.lst) and i >= 0

  @staticmethod
  def set(title, s, i_lst=[]):
    s = s.strip()
    if len(s) == 0:
      return
    if len(i_lst) == 0 or all(i not in title or not title[i] for i in i_lst):
      title.ti = s
      title.lst = csv_line_to_arr(s, title.delim)
    else:
      new_lst = csv_line_to_arr(s, title.delim)
      for i, x in enumerate(new_lst[:len(i_lst)]):
        if i_lst[i] in title:
          title.lst[i_lst[i]] = x.strip()
      title.ti = arr_to_csv_line(title.lst, title.delim)


class Title2(Title):
  def __init__(self, ti, delim=None):
    super().__init__(delim=delim)
    Title.set(self, ti)


class Unit:
  def __init__(self, item=None, lst=None):
    self._ti = item
    self.lst: List[Unit] = [] if lst is None else lst

  @property
  def item(self):
    return self._ti

  def reverse(self, predicate=lambda x: True):
    if len(self.lst) == 0:
      return [[self.item]]
    ans = []
    for x in self.lst:
      for y in x.reverse(predicate):
        ans.append([*y, self.item] if predicate(self.item) else y)
    return ans

  class Layer:
    def __init__(self, layer_lst):
      self.layer_lst = layer_lst

    def _raw_strlst(self):
      def all_len_variations_from_right(strs):
        if len(strs) <= 0: return []
        strs = strs[::-1]
        ans = [strs[0]]
        for s in strs[1:]:
          if s == "": continue
          ans.append("%s: %s" % (s, ans[-1]))
        return ans
      def pick_unique_names(name_lsts):
        def _f(name_lsts, st):
          d = {}
          for i, lst in enumerate(name_lsts):
            if st >= len(lst): continue
            name = lst[st]
            if name not in d: d[name] = []
            d[name].append(i)
          ans = [min(st, len(lst) - 1) for lst in name_lsts]
          for name in d:
            if len(d[name]) == 1: continue
            remapped_is = _f([name_lsts[idx] for idx in d[name]], st + 1)
            for idx, i in zip(d[name], remapped_is):
              ans[idx] = i
          return ans
        return [x[i] for x, i in zip(name_lsts, _f(name_lsts, 0))]
      lst = [([str(x) for x in titles], [str(x) for x in raw_subtitles])
             for titles, raw_subtitles in self.layer_lst]
      name_lsts = [all_len_variations_from_right(titles) for titles, _ in lst]
      names = pick_unique_names(name_lsts)
      subs = [raw_subtitles for _, raw_subtitles in lst]
      return [*zip(names, subs)]
    
    def _str(self):
      lst = self._raw_strlst()
      def str_layer_entry(layer_entry):
        title, raw_subtitles = layer_entry
        return title if len(raw_subtitles) == 0 else "%s\n%s" % (title, indent_forward("\n".join(raw_subtitles)))
      return "\n".join(str_layer_entry(le) for le in lst)

    def __str__(self):
      return self._str()

    def str_entries_with_sub(self):
      lst = self._raw_strlst()
      lst = [x for x in lst if len(x[1]) > 0]
      def str_layer_entry(layer_entry):
        title, raw_subtitles = layer_entry
        return title if len(raw_subtitles) == 0 else "%s\n%s" % (title, indent_forward("\n".join(raw_subtitles)))
      return "\n".join(str_layer_entry(le) for le in lst)

    def get_raw_subtitles(self):
      ans = []
      for titles, raw_subtitles in self.layer_lst:
        ans.extend(str(x) for x in raw_subtitles)
      return ans

  def _stratumise(self, predicate=lambda x: True):
    """
    returns: [layer_1, layer_2, ...]
      layer_n = [(title-lvl-n_1, [...raw-title-lvl-n+1]), (title-lvl-n_2, [...raw-title-lvl-n+1]), ...]
        title-lvl-n = [raw-title-lvl-1, raw-title-lvl-2, ...]
    """
    include_self = predicate(self.item)
    stratums = [x._stratumise() for x in self.lst]
    ans = [[] for _ in range(
        0 if len(stratums) == 0 else max(len(st) for st in stratums))]
    for i in range(1, len(ans)):
      ans[i] = []
    for st in stratums:
      for i, layer in enumerate(st):
        if include_self:
          for title, raw_titles in layer:
            title.insert(0, self.item)
        ans[i].extend(layer)
    if include_self:
      ans.insert(0, [([self.item], [x.item for x in self.lst])])
    return ans

  def stratumise(self, predicate=lambda x: True):
    return [Unit.Layer(x) for x in self._stratumise(predicate)]

  def __len__(self):
    return len(self.lst)

  def _str(self, stringify=str):
    def child_str(child):
      return indent_forward(stringify(child))

    if len(self.lst) == 0:
      return stringify(self.item)
    else:
      return "{}\n{}".format(self.item, '\n'.join(child_str(x) for x in self.lst))

  def __str__(self):
    return self._str()
