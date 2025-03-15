from typing import Iterable
import random


class Generator:
  def __init__(self, lst=[]):
    self.x = None
    self.set_lst(lst)

  def is_empty(self):
    return len(self._lst) == 0

  def reset(self):
    self.it = iter(self._lst)

  def set_lst(self, lst: Iterable):
    self._lst = [*lst]
    self.reset()

  @property
  def lst(self):
    return self._lst

  @property
  def curr(self):
    return self.x

  def next(self):
    try:
      self.x = next(self.it)
    except StopIteration:
      self.reset()
      self.x = next(self.it)
    return self.x

  def __len__(self):
    return len(self._lst)


class RdGenerator(Generator):
  def reset(self):
    lst2 = [*self.lst]
    random.shuffle(lst2)
    self.it = iter(lst2)

Generator.typ = 1
RdGenerator.typ = 2
