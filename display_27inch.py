"""
Rainbow Robotics — Display 2
Animation: Hyperspace warp — stars zoom from center leaving rainbow trails

Usage:
  python display_27inch.py                  # primary monitor
  python display_27inch.py --monitor 1      # second monitor (0-indexed)
  python display_27inch.py --x 1920 --y 0  # manual offset if screeninfo missing
"""
import tkinter as tk
import math
import random
import sys

COMPANY = "Rainbow Robotics"
BG = "#000005"

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

def hue_to_rgb(h):
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    q = 1 - f
    combos = [(1,f,0),(q,1,0),(0,1,f),(0,q,1),(f,0,1),(1,0,q)]
    r, g, b = combos[i % 6]
    return int(r*255), int(g*255), int(b*255)

def rgb(r, g, b):
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"


class Star:
    __slots__ = ("angle", "depth", "speed", "hue")

    def __init__(self):
        self.reset()

    def reset(self):
        self.angle = random.uniform(0, 2 * math.pi)
        self.depth = random.uniform(0.01, 1.0)
        self.speed = random.uniform(0.012, 0.035)
        self.hue = random.uniform(0, 1)

    def update(self):
        self.depth -= self.speed
        self.hue = (self.hue + 0.002) % 1.0
        if self.depth <= 0:
            self.reset()
            self.depth = 1.0

    def screen_pos(self, cx, cy, max_r):
        r = (1 - self.depth) * max_r
        return cx + r * math.cos(self.angle), cy + r * math.sin(self.angle)

    def trail_pos(self, cx, cy, max_r):
        r = min((1 - self.depth + self.speed * 6) * max_r, max_r * 1.2)
        return cx + r * math.cos(self.angle), cy + r * math.sin(self.angle)

    def brightness(self):
        return max(0, min(255, int((1 - self.depth) * 255)))


class App:
    def __init__(self, root, W, H):
        self.root = root
        self.W = W
        self.H = H
        self.cx = W // 2
        self.cy = H // 2
        self.max_r = math.hypot(W, H) * 0.55
        root.bind("<Escape>", lambda e: root.destroy())

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.stars = [Star() for _ in range(500)]
        self.star_items = [
            self.canvas.create_line(0, 0, 0, 0, fill="#ffffff", width=1)
            for _ in self.stars
        ]

        self._build_title()
        self.tick = 0
        self._animate()

    def _build_title(self):
        cx, cy = self.cx, self.cy
        for off, col in [(8,"#000820"),(4,"#001840"),(2,"#003060")]:
            self.canvas.create_text(cx+off, cy+off, text=COMPANY,
                font=("Impact", 96, "bold"), fill=col)
        self.title_id = self.canvas.create_text(
            cx, cy, text=COMPANY, font=("Impact", 96, "bold"), fill="#00eeff")
        self.sub_id = self.canvas.create_text(
            cx, cy + 70,
            text="A U T O M A T I O N  •  I N T E L L I G E N C E",
            font=("Courier New", 22, "bold"), fill="#003344")

    def _animate(self):
        self.tick += 1
        cx, cy = self.cx, self.cy

        for star, item in zip(self.stars, self.star_items):
            star.update()
            x1, y1 = star.screen_pos(cx, cy, self.max_r)
            x2, y2 = star.trail_pos(cx, cy, self.max_r)
            bright = star.brightness()
            r, g, b = hue_to_rgb(star.hue)
            scale = bright / 255
            color = rgb(int(r*scale), int(g*scale), int(b*scale))
            width = max(1, int((1 - star.depth) * 3))
            self.canvas.coords(item, x1, y1, x2, y2)
            self.canvas.itemconfig(item, fill=color, width=width)

        hue = (self.tick / 200) % 1.0
        r, g, b = hue_to_rgb(hue)
        self.canvas.itemconfig(self.title_id, fill=rgb(r, g, b))

        sub_bright = int(40 + 30 * math.sin(self.tick / 30))
        self.canvas.itemconfig(self.sub_id, fill=rgb(0, sub_bright, sub_bright+10))

        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.sub_id)

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
