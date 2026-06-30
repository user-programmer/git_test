"""
Rainbow Robotics — Display 3
Animation: Kaleidoscope of rotating geometric petals in rainbow colors
           with the company name morphing between colors at the top
"""
import tkinter as tk
import math

COMPANY = "Rainbow Robotics"
BG = "#000000"
NUM_ARMS = 8       # symmetry arms
LAYERS = 6         # concentric petal layers

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
        self.cy = self.H // 2 + 40   # shift center down a bit for title room

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        # pre-allocate polygon items: layers * arms * 2 (petal + inner)
        self.petals = []
        for layer in range(LAYERS):
            row = []
            for arm in range(NUM_ARMS):
                pid = self.canvas.create_polygon(0, 0, 0, 0, 0, 0,
                                                  fill="#000000", outline="")
                inner = self.canvas.create_polygon(0, 0, 0, 0, 0, 0,
                                                    fill="#000000", outline="")
                row.append((pid, inner))
            self.petals.append(row)

        # outer glow ring
        self.ring_items = []
        for _ in range(60):
            rid = self.canvas.create_oval(0, 0, 2, 2, fill="#ffffff", outline="")
            self.ring_items.append(rid)

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
            cx, y, text=COMPANY,
            font=("Impact", 80, "bold"), fill="#ffffff"
        )
        # decorative line under title
        self.bar_l = self.canvas.create_rectangle(
            cx - 380, y + 54, cx - 20, y + 58, fill="#aa00ff", outline=""
        )
        self.bar_r = self.canvas.create_rectangle(
            cx + 20, y + 54, cx + 380, y + 58, fill="#ff0088", outline=""
        )

    def _petal_points(self, cx, cy, angle_offset, radius, petal_w, n_points=12):
        pts = []
        for i in range(n_points + 1):
            t = i / n_points
            a = angle_offset + petal_w * (t - 0.5)
            r = radius * math.sin(t * math.pi) ** 0.7
            pts.append(cx + r * math.cos(a))
            pts.append(cy + r * math.sin(a))
        return pts

    def _animate(self):
        self.tick += 1
        t = self.tick / 60.0
        cx, cy = self.cx, self.cy

        symmetry_angle = (2 * math.pi) / NUM_ARMS
        petal_w = symmetry_angle * 0.72

        for li, layer_row in enumerate(self.petals):
            base_radius = 60 + li * 68
            rot_speed = (0.18 + li * 0.06) * (1 if li % 2 == 0 else -1)
            rotation = t * rot_speed

            for ai, (pid, inner_id) in enumerate(layer_row):
                arm_angle = ai * symmetry_angle + rotation
                hue = ((li / LAYERS) + (ai / NUM_ARMS) * 0.5 + t * 0.08) % 1.0
                r, g, b = hsv_to_rgb(hue, 0.9, 1.0)
                color = rgb(r, g, b)

                pts = self._petal_points(cx, cy, arm_angle, base_radius, petal_w, n_points=16)
                self.canvas.coords(pid, *pts)
                self.canvas.itemconfig(pid, fill=color, outline="")

                # inner bright petal (smaller)
                hue2 = (hue + 0.08) % 1.0
                r2, g2, b2 = hsv_to_rgb(hue2, 0.5, 1.0)
                inner_pts = self._petal_points(cx, cy, arm_angle, base_radius * 0.55, petal_w * 0.7, n_points=12)
                self.canvas.coords(inner_id, *inner_pts)
                self.canvas.itemconfig(inner_id, fill=rgb(r2, g2, b2), outline="")

        # rotating dot ring around entire kaleidoscope
        outer_r = 60 + (LAYERS - 1) * 68 + 50
        for i, rid in enumerate(self.ring_items):
            angle = (i / len(self.ring_items)) * 2 * math.pi + t * 0.4
            x = cx + outer_r * math.cos(angle)
            y = cy + outer_r * math.sin(angle)
            hue = (i / len(self.ring_items) + t * 0.05) % 1.0
            r, g, b = hsv_to_rgb(hue)
            bright = int(100 + 80 * math.sin(t * 3 + i * 0.2))
            col = rgb(int(r * bright / 255), int(g * bright / 255), int(b * bright / 255))
            sz = 2 + math.sin(t * 2 + i * 0.3)
            self.canvas.coords(rid, x - sz, y - sz, x + sz, y + sz)
            self.canvas.itemconfig(rid, fill=col)

        # title color pulse
        hue_t = (t * 0.15) % 1.0
        r, g, b = hsv_to_rgb(hue_t, 0.7, 1.0)
        self.canvas.itemconfig(self.title_id, fill=rgb(r, g, b))

        # bar color pulse
        hue_b = (hue_t + 0.5) % 1.0
        rb, gb, bb = hsv_to_rgb(hue_b)
        self.canvas.itemconfig(self.bar_l, fill=rgb(rb, gb, bb))
        hue_b2 = (hue_t + 0.75) % 1.0
        rb2, gb2, bb2 = hsv_to_rgb(hue_b2)
        self.canvas.itemconfig(self.bar_r, fill=rgb(rb2, gb2, bb2))

        # keep title above all
        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.bar_l)
        self.canvas.tag_raise(self.bar_r)

        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
