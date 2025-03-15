from core.parser import Parser 
from core.utils import levenshtein_ratio_and_distance, max_elem

class Kernel:
  def has_lst(self):
    return hasattr(self, 'd')

  def load_lst(self, txt):
    lst = Parser.parse_text(txt).lst
    d: dict[str, list[list[str]]] = {}
    for a in lst:
      for k in a:
        if k not in d:
          d[k] = []
        d[k].append(a)
    self.d = d

  def get_closest(self, keyword, N):
    mem = {}

    def calc_score(x):
      if x not in mem:
        mem[x] = levenshtein_ratio_and_distance(x, keyword)
      return mem[x]

    lst = [*self.d]
    res = [x for x in lst if keyword in x][:N]
    res.sort(key=len)
    for x in res: lst.remove(x)
    if len(res) < N:
      res2 = max_elem(lst, N - len(res), calc_score)
      res2.sort(key=calc_score, reverse=True)
      res.extend(res2)
    return [(x, self.d[x]) for x in res]
