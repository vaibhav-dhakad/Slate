#!/usr/bin/env python3
"""
Slate — matches screenshot UI
Run: python3 Notepad.py
Deps: sudo apt install python3-tk
"""

import tkinter as tk
from tkinter import messagebox
import json, os
from datetime import datetime

DATA = os.path.expanduser("~/.Slate.json")

# ── Colours ─────────────────────────────────────────────────────
SB_BG        = "#1e2535"
SB_CARD      = "#252e42"
SB_CARD_SEL  = "#2d3a56"
SB_CARD_HOV  = "#283248"
ED_BG        = "#1e1a16"
TB_BG        = "#252118"
TOP_BG       = "#161b2a"
TEXT_PRI     = "#dde3ef"
TEXT_SEC     = "#8b95a8"
TEXT_DATE    = "#6b7a92"
ACCENT_PUR   = "#c084fc"
ACCENT_BLUE  = "#60a5fa"
STAR_GOLD    = "#f59e0b"
DANGER       = "#f87171"
BORDER_SEL   = "#3d4f75"
BORDER_NOR   = "#2a3348"
INPUT_BG     = "#141926"
INPUT_BOR    = "#2a3348"
SCROLLBAR    = "#2a3044"
TOOLBAR_SEP  = "#3a3226"

def load():
    if os.path.exists(DATA):
        try:
            with open(DATA) as f: return json.load(f)
        except: pass
    return []

def save(notes):
    with open(DATA, "w") as f: json.dump(notes, f, indent=2)

def now_full():  return datetime.now().strftime("%b %d, %Y, %I:%M %p")
def now_short(): return datetime.now().strftime("%b %d, %Y")

def parse_font(fnt):
    """Parse 'Family Size [style]' string into tk font tuple."""
    parts = fnt.split()
    si = next(i for i, p in enumerate(parts) if p.isdigit())
    return tuple([" ".join(parts[:si]), int(parts[si])] + parts[si+1:])


class App:
    def __init__(self, root):
        self.root      = root
        self.root.title("Slate")
        self.root.geometry("1060x620")
        self.root.minsize(800, 500)
        self.root.configure(bg=TOP_BG)

        self.notes     = load()
        self.sel       = None
        self.filtered  = []
        self.sort_mode  = "modified"
        self.sq         = tk.StringVar()
        self.sq.trace("w", lambda *a: self.refresh())
        self._guard     = False
        self.batch_mode = False
        self.checked    = set()

        self._ui()
        self.refresh()
        if self.notes: self.pick(0)

    # ── BUILD UI ────────────────────────────────────────────────
    def _ui(self):
        # Top bar
        top = tk.Frame(self.root, bg=TOP_BG, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="🗒  Slate", bg=TOP_BG, fg=ACCENT_PUR,
                 font=("Georgia", 13, "bold")).pack(side="left", padx=16, pady=12)

        btn_f = tk.Frame(top, bg=TOP_BG)
        btn_f.pack(side="right", padx=14, pady=10)
        tk.Button(btn_f, text="+ New Note",
                  bg=ACCENT_PUR, fg="#0d0d1a",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=14, pady=5, bd=0,
                  activebackground="#a855f7", activeforeground="#fff",
                  command=self.new_note).pack(side="left")
        
        tk.Button(btn_f, text="▾",
                  bg="#a855f7", fg="#0d0d1a",
                  font=("Segoe UI", 9, "bold"), relief="ridge", cursor="hand2",
                  padx=6, pady=5, bd=0,
                  activebackground="#9333ea").pack(side="left")
        

        tk.Frame(self.root, bg="#0d1120", height=1).pack(fill="x")

        main = tk.Frame(self.root, bg=TOP_BG)
        main.pack(fill="both", expand=True)

        # ── Sidebar ─────────────────────────────────────────────
        sb = tk.Frame(main, bg=SB_BG, width=315)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Search bar
        sf = tk.Frame(sb, bg=SB_BG)
        sf.pack(fill="x", padx=10, pady=(10, 6))
        sw = tk.Frame(sf, bg=INPUT_BG,
                      highlightbackground=INPUT_BOR, highlightthickness=1)
        sw.pack(fill="x")
        tk.Label(sw, text="🔍", bg=INPUT_BG, fg=TEXT_SEC,
                 font=("Segoe UI", 10)).pack(side="left", padx=(8, 2))
        tk.Entry(sw, textvariable=self.sq, bg=INPUT_BG, fg=TEXT_PRI,
                 insertbackground=ACCENT_PUR, relief="flat",
                 font=("Segoe UI", 10), highlightthickness=0
                 ).pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(sw, text="✕", bg=INPUT_BG, fg=TEXT_SEC,
                  font=("Segoe UI", 9), relief="flat", cursor="hand2",
                  activebackground=INPUT_BG, bd=0,
                  command=lambda: self.sq.set("")
                  ).pack(side="right", padx=4)

        # Sort row
        sr = tk.Frame(sb, bg=SB_BG)
        sr.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(sr, text="Sort by:", bg=SB_BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8)).pack(side="left")
        self.sort_lbl = tk.Button(sr, text="Last Modified ▾",
                                  bg=SB_BG, fg=ACCENT_BLUE,
                                  font=("Segoe UI", 8), relief="flat",
                                  cursor="hand2", bd=0,
                                  activebackground=SB_BG,
                                  command=self.cycle_sort)
        self.sort_lbl.pack(side="left", padx=3)
        self.sel_btn = tk.Button(sr, text="Select",
                                 bg=SB_BG, fg=TEXT_SEC,
                                 font=("Segoe UI", 8), relief="flat",
                                 cursor="hand2", bd=0,
                                 activebackground=SB_BG,
                                 command=self.toggle_batch)
        self.sel_btn.pack(side="right")

        # Card list
        cf = tk.Frame(sb, bg=SB_BG)
        cf.pack(fill="both", expand=True)
        self.cv = tk.Canvas(cf, bg=SB_BG, highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(cf, orient="vertical", command=self.cv.yview,
                           bg=SB_BG, troughcolor=SB_BG, width=5,
                           relief="flat", bd=0)
        self.cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.cv.pack(side="left", fill="both", expand=True)
        self.cf2 = tk.Frame(self.cv, bg=SB_BG)
        self.cw  = self.cv.create_window((0, 0), window=self.cf2, anchor="nw")
        self.cf2.bind("<Configure>",
                      lambda e: self.cv.configure(scrollregion=self.cv.bbox("all")))
        self.cv.bind("<Configure>",
                     lambda e: self.cv.itemconfig(self.cw, width=e.width))
        self.cv.bind_all("<MouseWheel>",
                         lambda e: self.cv.yview_scroll(-1*(e.delta//120), "units"))

        # Batch delete bar (hidden until batch mode)
        self.batch_bar = tk.Frame(sb, bg="#2a1a1a")
        self.batch_lbl = tk.Label(self.batch_bar, text="0 selected",
                                  bg="#2a1a1a", fg=TEXT_SEC, font=("Segoe UI", 8))
        self.batch_lbl.pack(side="left", padx=10, pady=5)
        tk.Button(self.batch_bar, text="🗑 Delete Selected",
                  bg=DANGER, fg="#fff", font=("Segoe UI", 8, "bold"),
                  relief="flat", cursor="hand2", padx=8, pady=3, bd=0,
                  activebackground="#ef4444",
                  command=self.batch_delete).pack(side="right", padx=8, pady=4)

        # Bottom count bar
        self.bot = tk.Frame(sb, bg=SB_BG, height=28)
        self.bot.pack(fill="x")
        self.bot.pack_propagate(False)
        tk.Label(self.bot, text="Sort by:", bg=SB_BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8)).pack(side="left", padx=10, pady=6)
        self.count_lbl = tk.Label(self.bot, text="0 notes", bg=SB_BG,
                                  fg=TEXT_SEC, font=("Segoe UI", 8))
        self.count_lbl.pack(side="right", padx=10)

        # Divider
        tk.Frame(main, bg="#0d1120", width=1).pack(side="left", fill="y")

        # ── Editor ──────────────────────────────────────────────
        ed = tk.Frame(main, bg=ED_BG)
        ed.pack(side="left", fill="both", expand=True)

        # Title row
        tr = tk.Frame(ed, bg=ED_BG)
        tr.pack(fill="x", padx=28, pady=(22, 0))
        self.tv = tk.StringVar()
        self.te = tk.Entry(tr, textvariable=self.tv, bg=ED_BG, fg=TEXT_PRI,
                           insertbackground=ACCENT_PUR, relief="flat",
                           font=("Georgia", 24, "bold"), highlightthickness=0)
        self.te.pack(side="left", fill="x", expand=True)
        self.te.bind("<KeyRelease>", self.on_edit)

        # Meta row
        mr = tk.Frame(ed, bg=ED_BG)
        mr.pack(fill="x", padx=28, pady=(4, 0))
        self.meta_lbl = tk.Label(mr, text="", bg=ED_BG, fg=TEXT_DATE,
                                 font=("Segoe UI", 8))
        self.meta_lbl.pack(side="left")
        tk.Button(mr, text="🗑  Delete", bg=DANGER, fg="#fff",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  padx=10, pady=3, bd=0,
                  activebackground="#ef4444", activeforeground="#fff",
                  command=self.delete).pack(side="right")

        # Toolbar
        tb = tk.Frame(ed, bg=TB_BG, height=40)
        tb.pack(fill="x", pady=(10, 0))
        tb.pack_propagate(False)

        self.tb_btns = {}
        left_tools = [
            ("B",  "bold",   "Georgia 11 bold",  self.fmt_bold),
            ("I",  "italic", "Georgia 11 italic", self.fmt_italic),
            ("≡",  "ul",     "Segoe UI 13",       self.fmt_ul),
            ("⊟",  "ol",     "Segoe UI 13",       self.fmt_ol),
            ("🔗", "link",   "Segoe UI 11",       self.fmt_link),
            ("↗",  "ext",    "Segoe UI 11",       lambda: None),
            ("ℹ",  "info",   "Segoe UI 11",       lambda: None),
        ]
        for txt, key, fnt, cmd in left_tools:
            b = tk.Button(tb, text=txt, bg=TB_BG, fg=TEXT_PRI,
                          font=parse_font(fnt), relief="flat", cursor="hand2",
                          padx=9, pady=6, bd=0,
                          activebackground="#3a3226",
                          activeforeground=ACCENT_PUR,
                          command=cmd)
            b.pack(side="left", padx=1)
            self.tb_btns[key] = b

        tk.Frame(tb, bg=TOOLBAR_SEP, width=1).pack(side="left", fill="y", pady=8, padx=6)

        for txt, key in [("⤢", "fs"), ("📄", "exp")]:
            b = tk.Button(tb, text=txt, bg=TB_BG, fg=TEXT_SEC,
                          font=("Segoe UI", 11), relief="flat",
                          cursor="hand2", padx=9, pady=6, bd=0,
                          activebackground="#3a3226")
            b.pack(side="right", padx=1)
            self.tb_btns[key] = b

        tk.Frame(ed, bg=TOOLBAR_SEP, height=1).pack(fill="x")

        # Text area
        tw = tk.Frame(ed, bg=ED_BG)
        tw.pack(fill="both", expand=True)
        tsc = tk.Scrollbar(tw, bg=ED_BG, troughcolor=ED_BG,
                           relief="flat", width=7, bd=0,
                           activebackground=SCROLLBAR)
        tsc.pack(side="right", fill="y")
        self.txt = tk.Text(tw, bg=ED_BG, fg=TEXT_PRI,
                           insertbackground=ACCENT_PUR, relief="flat",
                           font=("Segoe UI", 11), wrap="word",
                           padx=28, pady=16, bd=0,
                           highlightthickness=0, spacing1=4, spacing3=4,
                           yscrollcommand=tsc.set, undo=True)
        self.txt.pack(fill="both", expand=True)
        tsc.config(command=self.txt.yview)
        self.txt.bind("<KeyRelease>", self.on_edit)

        # Text tags
        self.txt.tag_configure("bold",   font=("Segoe UI", 11, "bold"))
        self.txt.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        self.txt.tag_configure("h1",     font=("Georgia", 15, "bold"),
                               spacing1=10, spacing3=4)
        self.txt.tag_configure("link",   foreground=ACCENT_BLUE, underline=True)
        self.txt.tag_configure("bullet", lmargin1=24, lmargin2=36)

        # Bottom status bar
        bb = tk.Frame(ed, bg=TB_BG, height=30)
        bb.pack(fill="x")
        bb.pack_propagate(False)
        self.wc = tk.Label(bb, text="", bg=TB_BG, fg=TEXT_DATE,
                           font=("Segoe UI", 8))
        self.wc.pack(side="bottom", pady=8)

        self._editor_on(False)

    # ── CARDS ───────────────────────────────────────────────────
    def refresh(self):
        for w in self.cf2.winfo_children():
            w.destroy()

        q = self.sq.get().lower().strip()

        idx = list(enumerate(self.notes))
        if self.sort_mode == "modified":
            idx.sort(key=lambda x: x[1].get("updated", ""), reverse=True)
        elif self.sort_mode == "created":
            idx.sort(key=lambda x: x[1].get("created", ""), reverse=True)
        else:
            idx.sort(key=lambda x: x[1].get("title", "").lower())

        starred   = [(i, n) for i, n in idx if n.get("starred")]
        unstarred = [(i, n) for i, n in idx if not n.get("starred")]

        self.filtered = []
        for ri, note in starred + unstarred:
            t = note.get("title", "") or "Untitled"
            b = note.get("body", "")
            if q and q not in t.lower() and q not in b.lower():
                continue
            self.filtered.append(ri)
            self._card(ri, note)

        n = len(self.filtered)
        self.count_lbl.config(text=f"{n} note{'s' if n != 1 else ''}")

    def _card(self, ri, note):
        is_sel = (ri == self.sel)
        bg = SB_CARD_SEL if is_sel else SB_CARD

        outer = tk.Frame(self.cf2, bg=SB_BG)
        outer.pack(fill="x", padx=8, pady=3)

        bframe = tk.Frame(outer, bg=BORDER_SEL if is_sel else BORDER_NOR,
                          padx=1, pady=1)
        bframe.pack(fill="x")

        card = tk.Frame(bframe, bg=bg, cursor="hand2")
        card.pack(fill="x")

        # Top row: star + title + date
        tr = tk.Frame(card, bg=bg)
        tr.pack(fill="x", padx=10, pady=(8, 3))

        star_fg = STAR_GOLD if note.get("starred") else TEXT_DATE
        sl = tk.Label(tr, text="★", bg=bg, fg=star_fg,
                      font=("Segoe UI", 12), cursor="hand2")
        sl.pack(side="left")
        sl.bind("<Button-1>", lambda e, r=ri: self._star(r))

        if self.batch_mode:
            chk_txt = "☑" if ri in self.checked else "☐"
            ck = tk.Label(tr, text=chk_txt, bg=bg, fg=ACCENT_PUR,
                          font=("Segoe UI", 13), cursor="hand2")
            ck.pack(side="left", padx=(2, 0))
            ck.bind("<Button-1>", lambda e, r=ri: self._toggle_check(r))

        title = note.get("title", "") or "Untitled"
        tl = tk.Label(tr, text=title, bg=bg, fg=TEXT_PRI,
                      font=("Segoe UI", 10, "bold"), anchor="w")
        tl.pack(side="left", padx=(5, 4), fill="x", expand=True)

        d = note.get("updated", "")
        try: d = datetime.strptime(d, "%b %d, %Y, %I:%M %p").strftime("%b %d, %Y")
        except: pass
        dl = tk.Label(tr, text=d, bg=bg, fg=TEXT_DATE, font=("Segoe UI", 7))
        dl.pack(side="right")

        # Preview
        prev = note.get("body", "").replace("\n", " ")
        prev = (prev[:80] + "…") if len(prev) > 80 else prev
        pl = tk.Label(card, text=prev, bg=bg, fg=TEXT_SEC,
                      font=("Segoe UI", 9), anchor="w", justify="left",
                      wraplength=255)
        pl.pack(fill="x", padx=12, pady=(0, 8))

        # Hover / click bindings
        def click(e, r=ri): self.pick(r)

        def _set_bg(widget, color):
            try: widget.configure(bg=color)
            except: pass
            for ch in widget.winfo_children():
                _set_bg(ch, color)

        def enter(e):
            if not is_sel: _set_bg(card, SB_CARD_HOV)
        def leave(e):
            if not is_sel: _set_bg(card, SB_CARD)

        for w in [card, tr, pl, tl, dl]:
            w.bind("<Button-1>", click)
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

    # ── NOTE ACTIONS ────────────────────────────────────────────
    def pick(self, ri):
        self.sel    = ri
        note        = self.notes[ri]
        self._editor_on(True)
        self._guard = True

        self.tv.set(note.get("title", ""))
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", note.get("body", ""))

        for td in note.get("tags", []):
            try: self.txt.tag_add(td["n"], td["s"], td["e"])
            except: pass

        self.meta_lbl.config(text=f"🕐  Last edited: {note.get('updated', '')}")
        self._wc()
        self._guard = False
        self.refresh()

    def new_note(self):
        n = {"title": "", "body": "", "starred": False,
             "created": now_full(), "updated": now_full(), "tags": []}
        self.notes.insert(0, n)
        save(self.notes)
        self.sq.set("")
        self.refresh()
        self.pick(0)
        self.te.focus()

    def delete(self):
        if self.sel is None: return
        t = self.notes[self.sel].get("title", "Untitled") or "Untitled"
        if not messagebox.askyesno("Delete", f'Delete "{t}"?'): return
        self.notes.pop(self.sel)
        save(self.notes)
        self.sel = None
        self._editor_on(False)
        self.refresh()
        if self.notes: self.pick(0)

    def toggle_batch(self):
        self.batch_mode = not self.batch_mode
        self.checked.clear()
        self.sel_btn.config(text="Cancel" if self.batch_mode else "Select",
                            fg=DANGER if self.batch_mode else TEXT_SEC)
        if self.batch_mode:
            self.batch_bar.pack(fill="x", before=self.bot)
        else:
            self.batch_bar.pack_forget()
        self.refresh()

    def _toggle_check(self, ri):
        if ri in self.checked: self.checked.discard(ri)
        else:                  self.checked.add(ri)
        n = len(self.checked)
        self.batch_lbl.config(text=f"{n} selected")
        self.refresh()

    def batch_delete(self):
        if not self.checked: return
        if not messagebox.askyesno("Delete", f"Delete {len(self.checked)} note(s)?"): return
        self.notes = [n for i, n in enumerate(self.notes) if i not in self.checked]
        save(self.notes)
        self.checked.clear()
        self.sel = None
        self._editor_on(False)
        self.toggle_batch()
        if self.notes: self.pick(0)

    def _star(self, ri):
        self.notes[ri]["starred"] = not self.notes[ri].get("starred", False)
        save(self.notes)
        self.refresh()

    def on_edit(self, e=None):
        if self._guard or self.sel is None: return
        n = now_full()
        self.notes[self.sel]["title"]   = self.tv.get()
        self.notes[self.sel]["body"]    = self.txt.get("1.0", "end-1c")
        self.notes[self.sel]["updated"] = n
        td = []
        for tag in ("bold", "italic", "h1", "link", "bullet"):
            rng = self.txt.tag_ranges(tag)
            for i in range(0, len(rng), 2):
                td.append({"n": tag, "s": str(rng[i]), "e": str(rng[i+1])})
        self.notes[self.sel]["tags"] = td
        save(self.notes)
        self.meta_lbl.config(text=f"🕐  Last edited: {n}")
        self._wc()
        self.refresh()

    # ── FORMATTING ──────────────────────────────────────────────
    def _toggle_tag(self, tag):
        try:
            s = self.txt.index("sel.first")
            e = self.txt.index("sel.last")
        except tk.TclError: return
        rng = self.txt.tag_ranges(tag)
        covered = any(
            self.txt.compare(rng[i], "<=", s) and self.txt.compare(rng[i+1], ">=", e)
            for i in range(0, len(rng), 2))
        if covered: self.txt.tag_remove(tag, s, e)
        else:       self.txt.tag_add(tag, s, e)
        self.on_edit()

    def fmt_bold(self):   self._toggle_tag("bold")
    def fmt_italic(self): self._toggle_tag("italic")
    def fmt_link(self):   self._toggle_tag("link")

    def fmt_ul(self):
        try:
            ls  = self.txt.index("insert linestart")
            cur = self.txt.get(ls, ls + " 2c")
            if cur == "• ": self.txt.delete(ls, ls + " 2c")
            else:           self.txt.insert(ls, "• ")
        except: pass
        self.on_edit()

    def fmt_ol(self):
        try:
            ls = self.txt.index("insert linestart")
            self.txt.insert(ls, "1. ")
        except: pass
        self.on_edit()

    # ── SORT ────────────────────────────────────────────────────
    def cycle_sort(self):
        modes  = ["modified", "created", "title"]
        labels = {"modified": "Last Modified ▾",
                  "created":  "Date Created ▾",
                  "title":    "Title A–Z ▾"}
        self.sort_mode = modes[(modes.index(self.sort_mode) + 1) % 3]
        self.sort_lbl.config(text=labels[self.sort_mode])
        self.refresh()

    # ── HELPERS ─────────────────────────────────────────────────
    def _editor_on(self, on):
        s = "normal" if on else "disabled"
        self.te.config(state=s)
        self.txt.config(state=s)
        for b in self.tb_btns.values(): b.config(state=s)
        if not on:
            self.tv.set("")
            self.txt.config(state="normal")
            self.txt.delete("1.0", "end")
            self.txt.config(state="disabled")
            self.meta_lbl.config(text="")
            self.wc.config(text="")

    def _wc(self):
        c = self.txt.get("1.0", "end-1c")
        w = len(c.split()) if c.strip() else 0
        self.wc.config(text=f"{w} words · {len(c)} characters")


if __name__ == "__main__":
    root = tk.Tk()
    try: root.tk.call("tk", "scaling", 1.25)
    except: pass
    App(root)
    root.mainloop()
