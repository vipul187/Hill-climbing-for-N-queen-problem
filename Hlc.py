"""
N-Queens : Steepest-Ascent Hill Climbing + Random Restarts
LIVE animation in a Tkinter window (no GIFs, no extra installs).

State      : board[col] = row of queen in that column
Heuristic  : h = number of attacking queen pairs   (goal h == 0)
Neighbours : move ONE queen to another row in its own column
Rule       : take the neighbour with the lowest h.
             If no neighbour is better -> local minimum -> random restart.

Run:  python nqueens_hill_climbing_live.py
Keys: SPACE = play/pause   S = single step   R = new board
"""
import random
import tkinter as tk

# ---------------------------------------------------------- algorithm
def heuristic(board):
    n, h = len(board), 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == j - i:
                h += 1
    return h


def attacking_pairs(board):
    n = len(board)
    return [(i, j) for i in range(n) for j in range(i + 1, n)
            if board[i] == board[j] or abs(board[i] - board[j]) == j - i]


def neighbour_grid(board):
    """grid[row][col] = h if the queen of `col` moved to `row`."""
    n = len(board)
    grid = [[None] * n for _ in range(n)]
    best = float("inf")
    for c in range(n):
        orig = board[c]
        for r in range(n):
            if r == orig:
                continue
            board[c] = r
            grid[r][c] = heuristic(board)
            best = min(best, grid[r][c])
        board[c] = orig
    return grid, best


class HillClimber:
    """One call to step() = one move of the algorithm."""
    def __init__(self, n):
        self.n = n
        self.restarts = 0
        self.moves = 0
        self.history = []          # h values for the graph
        self.restart_marks = []    # indices where restarts happened
        self.new_start()

    def new_start(self):
        self.board = [random.randrange(self.n) for _ in range(self.n)]
        self.h = heuristic(self.board)
        self.history.append(self.h)
        self.state = "start"

    def step(self):
        """Returns (col, from_row, to_row) for a move, or None."""
        if self.h == 0:
            self.state = "solved"
            return None
        grid, best = neighbour_grid(self.board)
        if best >= self.h:                       # stuck
            self.state = "stuck"
            self.restarts += 1
            self.restart_marks.append(len(self.history) - 1)
            self.new_start()
            return "restart"
        options = [(c, r) for r in range(self.n) for c in range(self.n)
                   if grid[r][c] == best]
        c, r = random.choice(options)            # random tie-break
        frm = self.board[c]
        self.board[c] = r
        self.h = best
        self.moves += 1
        self.history.append(self.h)
        self.state = "solved" if self.h == 0 else "move"
        return (c, frm, r)


# ---------------------------------------------------------- animation (Tkinter)
LIGHT, DARK = "#f1dfb6", "#5aa786"
QUEEN, BAD, GOOD = "#1d2b26", "#d1452b", "#0f7a52"
BEST, BG = "#f6c445", "#faf6ee"
CELL = 70


class App:
    def __init__(self, root, n=8):
        self.root = root
        root.title("N-Queens · Hill Climbing (live)")
        root.configure(bg=BG)
        self.playing = True
        self.anim = None
        self.speed = tk.IntVar(value=500)        # ms between moves
        self.size = tk.IntVar(value=n)
        self.show_map = tk.BooleanVar(value=True)

        left = tk.Frame(root, bg=BG); left.pack(side="left", padx=16, pady=16)
        right = tk.Frame(root, bg=BG); right.pack(side="left", padx=16, pady=16, fill="y")

        self.board_cv = tk.Canvas(left, highlightthickness=0, bg=BG)
        self.board_cv.pack()

        self.h_lbl = tk.Label(right, font=("Consolas", 64, "bold"), bg=BG, fg=QUEEN)
        self.h_lbl.pack(anchor="w")
        tk.Label(right, text="h = attacking pairs", bg=BG, fg="#6b7a74",
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.stats = tk.Label(right, font=("Consolas", 12), bg=BG, fg=QUEEN, justify="left")
        self.stats.pack(anchor="w", pady=(8, 4))
        self.msg = tk.Label(right, font=("Segoe UI", 12, "bold"), bg=BG, wraplength=320,
                            justify="left")
        self.msg.pack(anchor="w", pady=4)

        self.graph = tk.Canvas(right, width=340, height=150, bg="#f3ecdd", highlightthickness=0)
        self.graph.pack(anchor="w", pady=8)

        btns = tk.Frame(right, bg=BG); btns.pack(anchor="w", pady=6)
        self.play_btn = tk.Button(btns, text="Pause", width=8, command=self.toggle)
        self.play_btn.pack(side="left", padx=2)
        tk.Button(btns, text="Step", width=8, command=self.manual_step).pack(side="left", padx=2)
        tk.Button(btns, text="New board", width=10, command=self.reset).pack(side="left", padx=2)

        row = tk.Frame(right, bg=BG); row.pack(anchor="w", pady=4)
        tk.Label(row, text="N =", bg=BG).pack(side="left")
        tk.Spinbox(row, from_=4, to=14, width=4, textvariable=self.size,
                   command=self.reset).pack(side="left", padx=4)
        tk.Checkbutton(row, text="show neighbour h", variable=self.show_map, bg=BG,
                       command=self.redraw).pack(side="left", padx=8)
        tk.Scale(right, from_=1200, to=80, orient="horizontal", label="speed",
                 variable=self.speed, bg=BG, length=300, showvalue=False).pack(anchor="w")

        root.bind("<space>", lambda e: self.toggle())
        root.bind("s", lambda e: self.manual_step())
        root.bind("r", lambda e: self.reset())
        self.reset()

    # ---------- setup
    def reset(self):
        if self.anim:
            self.root.after_cancel(self.anim); self.anim = None
        self.n = max(4, min(14, int(self.size.get())))
        self.cell = max(36, min(CELL, 560 // self.n))
        side = self.cell * self.n
        self.board_cv.config(width=side, height=side)
        self.hc = HillClimber(self.n)
        self.busy = False
        self.redraw()
        if self.playing:
            self.schedule()

    # ---------- drawing
    def xy(self, col, row):
        """centre pixel of a square (row 0 at bottom)."""
        return (col + .5) * self.cell, (self.n - row - .5) * self.cell

    def redraw(self, flash=None):
        cv, n, s, b = self.board_cv, self.n, self.cell, self.hc.board
        cv.delete("all")
        grid, best = neighbour_grid(b[:])
        for r in range(n):
            for c in range(n):
                x0, y0 = c * s, (n - 1 - r) * s
                color = DARK if (r + c) % 2 == 0 else LIGHT
                is_best = grid[r][c] == best and best < self.hc.h
                cv.create_rectangle(x0, y0, x0 + s, y0 + s, fill=color, width=0)
                if self.show_map.get() and grid[r][c] is not None:
                    if is_best:
                        cv.create_rectangle(x0 + 5, y0 + 5, x0 + s - 5, y0 + s - 5,
                                            fill=BEST, width=0, tags="best")
                    cv.create_text(x0 + s / 2, y0 + s / 2, text=str(grid[r][c]),
                                   font=("Consolas", max(8, s // 5), "bold" if is_best else ""),
                                   fill=QUEEN if is_best else "#3d4a45")
        pairs = attacking_pairs(b)
        for i, j in pairs:
            cv.create_line(*self.xy(i, b[i]), *self.xy(j, b[j]),
                           fill=BAD, width=3, capstyle="round", tags="attack")
        bad = {c for p in pairs for c in p}
        self.queen_ids = []
        for c, r in enumerate(b):
            x, y = self.xy(c, r)
            color = GOOD if self.hc.h == 0 else (BAD if c in bad else QUEEN)
            qid = cv.create_text(x, y, text="\u265B", font=("Segoe UI Symbol", int(s * .55)),
                                 fill=color)
            self.queen_ids.append(qid)
        if self.hc.h == 0:
            cv.create_rectangle(3, 3, n * s - 3, n * s - 3, outline=GOOD, width=6)
        if flash:
            cv.create_rectangle(0, 0, n * s, n * s, fill=BAD, stipple="gray25",
                                width=0, tags="flash")
        self.pulse_best()
        self.update_panel()

    def pulse_best(self, k=0):
        """gentle blink of the 'best next move' squares."""
        if not self.board_cv.find_withtag("best"):
            return
        self.board_cv.itemconfig("best", fill=BEST if k % 2 == 0 else "#fbe3a0")
        self.root.after(450, lambda: self.pulse_best(k + 1))

    def update_panel(self):
        hc = self.hc
        self.h_lbl.config(text=str(hc.h), fg=GOOD if hc.h == 0 else QUEEN)
        self.stats.config(text=f"N        : {self.n}\nrestarts : {hc.restarts}\nmoves    : {hc.moves}")
        text, col = {
            "start":  ("Random start. Checking every single-queen move...", QUEEN),
            "move":   ("Took the steepest downhill move.", QUEEN),
            "stuck":  ("Local minimum! No better neighbour -> random restart.", BAD),
            "solved": ("SOLVED! h = 0, no queen attacks another.", GOOD),
        }[hc.state]
        self.msg.config(text=text, fg=col)
        self.draw_graph()

    def draw_graph(self):
        g, hist = self.graph, self.hc.history
        g.delete("all")
        W, H, P = 340, 150, 10
        top = max(max(hist), 1)
        span = max(len(hist) - 1, 10)
        x = lambda i: P + i / span * (W - 2 * P)
        y = lambda h: P + (1 - h / top) * (H - 2 * P)
        for m in self.hc.restart_marks:
            g.create_line(x(m), P, x(m), H - P, fill=BAD, dash=(3, 3))
        if len(hist) > 1:
            pts = [v for i, h in enumerate(hist) for v in (x(i), y(h))]
            g.create_polygon(x(0), H - P, *pts, x(len(hist) - 1), H - P,
                             fill="#d5e3e8", outline="")
            g.create_line(*pts, fill="#2f6f9f", width=2.5)
        cx, cy = x(len(hist) - 1), y(hist[-1])
        g.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#2f6f9f", outline="")
        g.create_text(P + 2, P, text="h over time (red = restart)", anchor="nw",
                      fill="#6b7a74", font=("Segoe UI", 9))

    # ---------- animation of one move: queen glides to new row
    def glide(self, col, frm, to, frames=14, k=0):
        cv = self.board_cv
        if k == 0:
            cv.delete("attack")                       # attack lines fade out
            cv.itemconfig(self.queen_ids[col], fill=BEST)
        x0, y0 = self.xy(col, frm)
        _, y1 = self.xy(col, to)
        t = k / frames
        ease = 1 - (1 - t) ** 3                       # ease-out cubic
        cv.coords(self.queen_ids[col], x0, y0 + (y1 - y0) * ease)
        cv.tag_raise(self.queen_ids[col])
        if k < frames:
            self.root.after(16, lambda: self.glide(col, frm, to, frames, k + 1))
        else:
            self.busy = False
            self.redraw()
            if self.playing:
                self.schedule()

    def flash_restart(self, k=0):
        if k < 4:
            self.board_cv.itemconfig("flash", state="normal" if k % 2 == 0 else "hidden")
            self.root.after(120, lambda: self.flash_restart(k + 1))
        else:
            self.busy = False
            self.redraw()
            if self.playing:
                self.schedule()

    # ---------- control
    def do_step(self):
        if self.busy or self.hc.state == "solved":
            return
        result = self.hc.step()
        if result is None:
            self.redraw()
        elif result == "restart":
            self.busy = True
            self.hc.state = "stuck"
            self.redraw(flash=True)
            self.flash_restart()
        else:
            self.busy = True
            self.update_panel()
            self.glide(*result)

    def schedule(self):
        if self.hc.state == "solved":
            self.playing = False
            self.play_btn.config(text="Play")
            return
        self.anim = self.root.after(self.speed.get(), self.auto)

    def auto(self):
        self.anim = None
        if self.playing:
            self.do_step()

    def toggle(self):
        if self.hc.state == "solved":
            self.playing = True
            self.play_btn.config(text="Pause")
            self.reset()
            return
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")
        if self.playing and not self.busy:
            self.schedule()
        elif self.anim:
            self.root.after_cancel(self.anim); self.anim = None

    def manual_step(self):
        if self.playing:
            self.toggle()
        self.do_step()


if __name__ == "__main__":
    root = tk.Tk()
    App(root, n=8)
    root.mainloop()
