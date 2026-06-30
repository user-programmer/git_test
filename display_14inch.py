"""
Rainbow Robotics — Display 1
Animation: Continuous rainbow fireworks bursting across the screen

Usage:
  python display_14inch.py                  # primary monitor
  python display_14inch.py --monitor 1      # second monitor (0-indexed)
  python display_14inch.py --x 1920 --y 0  # manual offset if screeninfo missing
"""
import tkinter as tk
import math
import random
import sys

COMPANY = "Rainbow Robotics"
BG = "#000000"

PALETTE = [
    "#ff0044", "#ff4400", "#ffaa00", "#ffee00",
    "#00ff88", "#00ddff", "#0088ff", "#aa00ff", "#ff00cc",
]

# ── monitor targeting ────────────────────────────────────────────────────────

def parse_args():
    args = sys.argv[1:]
    monitor = 0
    x = y = None
    try:
        if "--monitor" in args:
            monitor = int(args[args.index("--monitor") + 1])
        if "--x" in args:
            x = int(args[args.index("--x") + 1])
        if "--y" in args:
            y = int(args[args.index("--y") + 1])
    except (IndexError, ValueError):
        pass
    return monitor, x, y

def get_monitor_rect(index, manual_x, manual_y):
    """Return (x, y, w, h) for the requested monitor, or None to fall back."""
    if manual_x is not None:
        # user supplied offset manually; use full screen size as fallback dims
        return manual_x, manual_y or 0, None, None
    try:
        from screeninfo import get_monitors
        monitors = get_monitors()
        if index < len(monitors):
            m = monitors[index]
            return m.x, m.y, m.width, m.height
        print(f"Monitor {index} not found — {len(monitors)} monitor(s) detected.")
    except ImportError:
        print("screeninfo not installed. Run: pip install screeninfo")
        print("Or use --x / --y to supply the monitor's top-left pixel offset.")
    return None

def place_window(root, index, manual_x, manual_y):
    rect = get_monitor_rect(index, manual_x, manual_y)
    if rect:
        x, y, w, h = rect
        if w and h:
            root.geometry(f"{w}x{h}+{x}+{y}")
        else:
            # partial info — maximise then move
            root.update_idletasks()
            root.geometry(f"+{x}+{y}")
        root.overrideredirect(True)   # borderless, stays on target monitor
        return w or root.winfo_screenwidth(), h or root.winfo_screenheight()
    else:
        # fallback: normal fullscreen on whatever is primary
        root.attributes("-fullscreen", True)
        return root.winfo_screenwidth(), root.winfo_screenheight()

# ── spark / firework classes ─────────────────────────────────────────────────

class Spark:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 6.5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.max_life = random.randint(40, 90)
        self.life = 0
        self.color = color
        self.size = random.uniform(1.5, 3.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.vx *= 0.97
        self.life += 1
        return self.life < self.max_life

    def alpha_color(self):
        t = 1 - self.life / self.max_life
        r = int(int(self.color[1:3], 16) * t)
        g = int(int(self.color[3:5], 16) * t)
        b = int(int(self.color[5:7], 16) * t)
        return f"#{max(0,r):02x}{max(0,g):02x}{max(0,b):02x}"


class Firework:
    def __init__(self, w, h):
        self.x = random.uniform(w * 0.15, w * 0.85)
        self.y = h
        self.ty = random.uniform(h * 0.1, h * 0.55)
        self.vy = -random.uniform(8, 14)
        self.color = random.choice(PALETTE)
        self.exploded = False
        self.sparks = []

    def update(self, w, h):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.ty:
                self.exploded = True
                for _ in range(random.randint(80, 150)):
                    self.sparks.append(Spark(self.x, self.y, self.color))
        else:
            self.sparks = [s for s in self.sparks if s.update()]
        return not self.exploded or len(self.sparks) > 0


class App:
    def __init__(self, root, W, H):
        self.root = root
        self.W = W
        self.H = H
        root.bind("<Escape>", lambda e: root.destroy())

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.fireworks = []
        self.sparks_on_canvas = {}
        self.tick = 0

        self._draw_title()
        self._animate()

    def _draw_title(self):
        cx = self.W // 2
        for off, col in [(6, "#330011"), (3, "#660022")]:
            self.canvas.create_text(cx + off, 70 + off, text=COMPANY,
                font=("Impact", 72, "bold"), fill=col)
        self.title_id = self.canvas.create_text(
            cx, 70, text=COMPANY, font=("Impact", 72, "bold"), fill="#ffffff")
        self.uline = self.canvas.create_rectangle(
            cx - 340, 115, cx + 340, 120, fill="#ff0044", outline="")

    def _animate(self):
        self.tick += 1
        W, H = self.W, self.H

        if self.tick % 18 == 0 or len(self.fireworks) < 3:
            self.fireworks.append(Firework(W, H))

        new_fws = []
        all_sparks = []
        for fw in self.fireworks:
            if fw.update(W, H):
                new_fws.append(fw)
                all_sparks.extend(fw.sparks)
        self.fireworks = new_fws

        active_ids = {id(s) for s in all_sparks}
        for sid in list(self.sparks_on_canvas):
            if sid not in active_ids:
                self.canvas.delete(self.sparks_on_canvas.pop(sid))

        for s in all_sparks:
            col = s.alpha_color()
            sz = s.size
            sid = id(s)
            if sid in self.sparks_on_canvas:
                oid = self.sparks_on_canvas[sid]
                self.canvas.coords(oid, s.x-sz, s.y-sz, s.x+sz, s.y+sz)
                self.canvas.itemconfig(oid, fill=col)
            else:
                oid = self.canvas.create_oval(
                    s.x-sz, s.y-sz, s.x+sz, s.y+sz, fill=col, outline="")
                self.sparks_on_canvas[sid] = oid

        for fw in self.fireworks:
            if not fw.exploded:
                self.canvas.create_oval(fw.x-2, fw.y-2, fw.x+2, fw.y+2,
                                        fill=fw.color, outline="")

        phase = (self.tick / 40) % 1.0
        n = len(PALETTE)
        idx = int(phase * n)
        self.canvas.itemconfig(self.title_id, fill=PALETTE[idx % n])
        self.canvas.itemconfig(self.uline, fill=PALETTE[(idx + 3) % n])
        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.uline)

        self.root.after(16, self._animate)


if __name__ == "__main__":
    monitor_idx, manual_x, manual_y = parse_args()
    root = tk.Tk()
    root.title("Rainbow Robotics")
    root.configure(bg=BG)
    root.update_idletasks()
    W, H = place_window(root, monitor_idx, manual_x, manual_y)
    App(root, W, H)
    root.mainloop()
