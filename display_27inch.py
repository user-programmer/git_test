"""
Rainbow Robotics — Display 2
Animation: Hyperspace warp — stars zoom from center leaving rainbow trails,
           company name glows in the middle
"""
import tkinter as tk
import math
import random

COMPANY = "Rainbow Robotics"
BG = "#000005"

def hue_to_rgb(h):
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    q = 1 - f
    combos = [
        (1, f, 0), (q, 1, 0), (0, 1, f),
        (0, q, 1), (f, 0, 1), (1, 0, q),
    ]
    r, g, b = combos[i % 6]
    return int(r * 255), int(g * 255), int(b * 255)

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
        x = cx + r * math.cos(self.angle)
        y = cy + r * math.sin(self.angle)
        return x, y

    def trail_pos(self, cx, cy, max_r):
        r = (1 - self.depth + self.speed * 6) * max_r
        r = min(r, max_r * 1.2)
        x = cx + r * math.cos(self.angle)
        y = cy + r * math.sin(self.angle)
        return x, y

    def brightness(self):
        return max(0, min(255, int((1 - self.depth) * 255)))


class App:
    def __init__(self, root):
        self.root = root
        root.title("Rainbow Robotics")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda e: root.destroy())

        self.W = root.winfo_screenwidth()
        self.H = root.winfo_screenheight()
        self.cx = self.W // 2
        self.cy = self.H // 2
        self.max_r = math.hypot(self.W, self.H) * 0.55

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.stars = [Star() for _ in range(500)]
        # spread initial depths
        for s in self.stars:
            s.depth = random.uniform(0.01, 1.0)

        self.star_items = []
        for _ in self.stars:
            line = self.canvas.create_line(0, 0, 0, 0, fill="#ffffff", width=1)
            self.star_items.append(line)

        self._build_title()
        self.tick = 0
        self._animate()

    def _build_title(self):
        cx, cy = self.cx, self.cy
        # layered glow
        for off, col in [(8, "#000820"), (4, "#001840"), (2, "#003060")]:
            self.canvas.create_text(cx + off, cy + off, text=COMPANY,
                font=("Impact", 96, "bold"), fill=col)
        self.title_id = self.canvas.create_text(
            cx, cy, text=COMPANY,
            font=("Impact", 96, "bold"), fill="#00eeff"
        )
        self.sub_id = self.canvas.create_text(
            cx, cy + 70,
            text="A U T O M A T I O N  •  I N T E L L I G E N C E",
            font=("Courier New", 22, "bold"),
            fill="#003344"
        )

    def _animate(self):
        self.tick += 1
        cx, cy = self.cx, self.cy

        for i, (star, item) in enumerate(zip(self.stars, self.star_items)):
            star.update()
            x1, y1 = star.screen_pos(cx, cy, self.max_r)
            x2, y2 = star.trail_pos(cx, cy, self.max_r)
            bright = star.brightness()
            r, g, b = hue_to_rgb(star.hue)
            scale = bright / 255
            color = rgb(int(r * scale), int(g * scale), int(b * scale))
            width = max(1, int((1 - star.depth) * 3))
            self.canvas.coords(item, x1, y1, x2, y2)
            self.canvas.itemconfig(item, fill=color, width=width)

        # pulse title color through hues
        hue = (self.tick / 200) % 1.0
        r, g, b = hue_to_rgb(hue)
        self.canvas.itemconfig(self.title_id, fill=rgb(r, g, b))

        # sub text dim pulse
        sub_bright = int(40 + 30 * math.sin(self.tick / 30))
        self.canvas.itemconfig(self.sub_id, fill=rgb(0, sub_bright, sub_bright + 10))

        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.sub_id)

        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
