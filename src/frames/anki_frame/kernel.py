import random
from core.generator import Generator


class Item:
  def __init__(self, s):
    self.s = s
    self.level = 0

  def __str__(self):
    return self.s


class Batch(Generator):
  def get_all_items(self, lower_lvl=0, higher_lvl=None):
    l, h = lower_lvl, higher_lvl
    ans = [x for x in self if l <= x.level]
    return ans if h is None else [x for x in self if x.level <= h]

  def set_level(self, lower, higher):
    self.lower_lvl, self.higher_lvl = lower, higher
    self.set_lst(self.get_all_items(lower, higher))

  def next(self):
    if self.curr.level < self.lower_lvl or self.curr.level > self.higher_lvl:
      self._lst.remove(self.curr)
    return super().next()


class Kernel:
  def __init__(self):
    self._batches = []
    self._settings = {
        'lowest_stage': 0,
        'highest_stage': 5,
        'batch_size': 10,
    }
    self._history = []
    self._his_i = 0
    self.item_count = 0
    self.curr_batch = None

  @property
  def settings(self):
    return self._settings

  @settings.setter
  def settings(self, s):
    self._settings = s

  @property
  def batches(self):
    return self._batches

  @batches.setter
  def batches(self, bs):
    self._batches = bs

  @property
  def items(self):
    ans = []
    for b in self.batches:
      ans.extend(b.get_all_items())
    return ans

  def get_setting(self, name):
    return self._settings[name]

  @property
  def _lvl_range(self):
    return self._settings['lowest_stage'], self._settings['highest_stage']

  @property
  def _batch_size(self):
    return self._settings['batch_size']

  def _sort_batches(self):
    l, h = self._lvl_range
    self._batches.sort(key=lambda x: len(x.get_all_items(l, h)))

  def _gen_new_batch(self, *params):
    b = Batch(*params)
    l, h = self._lvl_range
    b.set_level(l, h)
    return b

  def add_txt(self, txt):
    if len(self._batches) == 0 or len(self._batches[-1]) >= self.get_setting('batch_size'):
      self._batches.append(self._gen_new_batch())
    self._batches[-1].append(Item(txt))
    self.item_count += 1

  def switch_batch(self):
    l, h = self._lvl_range
    idx = 0 if self.curr_batch is None else self._batches.index(
        self.curr_batch)
    for i in range(len(self._batches)):
      i = (idx + i + 1) % len(self._batches)
      b = self._batches[i]
      if len(b.get_all_items(l, h)) > 0:
        self.curr_batch = b
        return b
    self.curr_batch = None
    return None

  def _next(self):
    try:
      return self.curr_batch.next()
    except StopIteration:
      self.switch_batch()
      return self.curr_batch.next()

  def next(self):
    self._his_i += 1
    if self._his_i < len(self._history):
      return self._history[self._his_i]
    ans = self._next()
    self._history.append(ans)
    return ans

  def prev(self):
    if self._his_i <= 0:
      raise Exception()
    self._his_i -= 1
    return self.curr()

  def curr(self):
    return self._history[self._his_i]

  def regroup(self):
    l, h = self._lvl_range
    itms = self.items
    batch_count = len(itms) // self._batch_size
    ins = [x for x in itms if l <= x.level <= h]
    outs = [x for x in itms if x not in ins]
    ins_count, outs_count = len(ins) // batch_count, len(outs) // batch_count
    random.shuffle(ins)
    random.shuffle(outs)
    batches = []
    for i in range(batch_count):
      b = self._gen_new_batch([*ins[i * ins_count: (i + 1) * ins_count],
                               *outs[i * outs_count: (i + 1) * outs_count]])
      batches.append(b)
    self.batches = batches

  @property
  def progress(self):
    pass
