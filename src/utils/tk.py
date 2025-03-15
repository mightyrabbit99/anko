import tkinter as tk

def text_sel_all(txt: tk.Text):
    txt.tag_add(tk.SEL, "1.0", tk.END)
    txt.mark_set(tk.INSERT, "1.0")
    txt.see(tk.INSERT)
    return 'break'

def text_copy_sel(txt: tk.Text):
    k = txt.index(tk.SEL_FIRST)
    if k == "None": return 'break'
    txt.clipboard_clear()
    txt.clipboard_append(txt.get(tk.SEL_FIRST, tk.SEL_LAST))
    return 'break'
