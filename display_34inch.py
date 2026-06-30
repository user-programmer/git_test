"""
Rainbow Robotics — Display 3
Animation: Kaleidoscope of rotating geometric petals in rainbow colors

Usage:
  python display_34inch.py                  # primary monitor
  python display_34inch.py --monitor 2      # third monitor (0-indexed)
  python display_34inch.py --x 3840 --y 0  # manual offset if screeninfo missing
"""
import tkinter as tk
import math
import sys

COMPANY = "Rainbow Robotics"
BG = "#000000"
NUM_ARMS = 8
LAYERS = 6

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
    if manual_x is not None:
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
            root.update_idletasks()
            root.geometry(f"+{x}+{y}")
        root.overrideredirect(True)
        return w or root.winfo_screenwidth(), h or root.winfo_screenheight()
    else:
        root.attributes("-fullscreen", True)
        return root.winfo_screenwidth(), root.winfo_screenheight()

# ── helpers ──────────────────────────────────────────────────────────────────

def hsv_to_rgb(h, s=1.0, v=1.0):
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    combos = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)]
    r, g, b = combos[i % 6]
    return int(r*255), int(g*255), int(b*255)

def rgb(r, g, b):
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

def lerp(a, b, t):
    return a + (b - a) * t


class App:
    def __init__(self, root, W, H):
        self.root = root
        self.W = W
        self.H = H
        self.cx = W // 2
        self.cy = H // 2 + 40
        root.bind("<Escape>", lambda e: root.destroy())

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.petals = []
        for _ in range(LAYERS):
            row = []
            for _ in range(NUM_ARMS):
                pid = self.canvas.create_polygon(0,0,0,0,0,0, fill="#000", outline="")
                inner = self.canvas.create_polygon(0,0,0,0,0,0, fill="#000", outline="")
                row.append((pid, inner))
            self.petals.append(row)

        self.ring_items = [
            self.canvas.create_oval(0,0,2,2, fill="#fff", outline="")
            for _ in range(60)
        ]

        self._build_title()
        self.tick = 0
        self._animate()

    def _build_title(self):
        cx = self.W // 2
        y = 72
        for off, col in [(6,"#1a0020"),(3,"#330033"),(1,"#660066")]:
            self.canvas.create_text(cx+off, y+off, text=COMPANY,
                font=("Impact", 80, "bold"), fill=col)
        self.title_id = self.canvas.create_text(
            cx, y, text=COMPANY, font=("Impact", 80, "bold"), fill="#ffffff")
        self.bar_l = self.canvas.create_rectangle(
            cx-380, y+54, cx-20, y+58, fill="#aa00ff", outline="")
        self.bar_r = self.canvas.create_rectangle(
            cx+20, y+54, cx+380, y+58, fill="#ff0088", outline="")

    def _petal_points(self, cx, cy, angle_offset, radius, petal_w, n=16):
        pts = []
        for i in range(n + 1):
            t = i / n
            a = angle_offset + petal_w * (t - 0.5)
            r = radius * math.sin(t * math.pi) ** 0.7
            pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
        return pts

    def _animate(self):
        self.tick += 1
        t = self.tick / 60.0
        cx, cy = self.cx, self.cy
        sym = (2 * math.pi) / NUM_ARMS
        petal_w = sym * 0.72

        for li, layer_row in enumerate(self.petals):
            base_r = 60 + li * 68
            rot = t * (0.18 + li * 0.06) * (1 if li % 2 == 0 else -1)
            for ai, (pid, inner_id) in enumerate(layer_row):
                arm_angle = ai * sym + rot
                hue = ((li / LAYERS) + (ai / NUM_ARMS) * 0.5 + t * 0.08) % 1.0
                self.canvas.coords(pid, *self._petal_points(cx, cy, arm_angle, base_r, petal_w))
                self.canvas.itemconfig(pid, fill=rgb(*hsv_to_rgb(hue, 0.9, 1.0)), outline="")
                hue2 = (hue + 0.08) % 1.0
                self.canvas.coords(inner_id, *self._petal_points(cx, cy, arm_angle, base_r*0.55, petal_w*0.7, n=12))
                self.canvas.itemconfig(inner_id, fill=rgb(*hsv_to_rgb(hue2, 0.5, 1.0)), outline="")

        outer_r = 60 + (LAYERS - 1) * 68 + 50
        for i, rid in enumerate(self.ring_items):
            angle = (i / len(self.ring_items)) * 2 * math.pi + t * 0.4
            x = cx + outer_r * math.cos(angle)
            y = cy + outer_r * math.sin(angle)
            hue = (i / len(self.ring_items) + t * 0.05) % 1.0
            r, g, b = hsv_to_rgb(hue)
            bright = int(100 + 80 * math.sin(t * 3 + i * 0.2))
            col = rgb(int(r*bright/255), int(g*bright/255), int(b*bright/255))
            sz = 2 + math.sin(t * 2 + i * 0.3)
            self.canvas.coords(rid, x-sz, y-sz, x+sz, y+sz)
            self.canvas.itemconfig(rid, fill=col)

        hue_t = (t * 0.15) % 1.0
        self.canvas.itemconfig(self.title_id, fill=rgb(*hsv_to_rgb(hue_t, 0.7, 1.0)))
        self.canvas.itemconfig(self.bar_l, fill=rgb(*hsv_to_rgb((hue_t+0.5)%1.0)))
        self.canvas.itemconfig(self.bar_r, fill=rgb(*hsv_to_rgb((hue_t+0.75)%1.0)))
        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.bar_l)
        self.canvas.tag_raise(self.bar_r)

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
