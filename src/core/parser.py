from .utils import Unit, Title, csv_line_to_arr
import io


class Parser:
  @staticmethod
  def parse_text(txt, delim=";"):
    def filter_line(l):
      ll = l.strip()
      return len(ll) > 0 and ll[:2] != "//"

    def indent(l):
      return l.find(l.strip())

    def parse_unit(lst, delim=";"):
      unit_stack, last_ind = [(-1, Unit())], -1
      for ind, arr in lst:
        title_ind, curr = unit_stack[-1]
        if ind > last_ind and len(curr.lst) > 0:
          unit_stack.append((last_ind, curr.lst[-1]))
        elif ind < last_ind and len(unit_stack) > 1:
          while ind <= title_ind and len(unit_stack) > 1:
            unit_stack.pop(-1)
            title_ind, curr = unit_stack[-1]
        title_ind, curr = unit_stack[-1]
        curr.lst.append(Unit(Title(arr, delim)))
        last_ind = ind
      return unit_stack[0][1]

    lines = [l for l in txt.split("\n") if filter_line(l)]
    inds = [indent(l) for l in lines]
    arrs = [csv_line_to_arr(l.strip(), delim) for l in lines]
    return parse_unit(zip(inds, arrs), delim)

  @staticmethod
  def parse_file(file: io.FileIO, delim=";"):
    return Parser.parse_text(file.read(), delim)
