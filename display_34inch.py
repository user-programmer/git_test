"""
Rainbow Robotics — 34-inch Display
Animation: Futuristic HUD / circuit-board style with particle streams,
           glitching scanlines, and a pulsing 3-D perspective title
"""
import tkinter as tk
import math
import random

COMPANY = "Rainbow Robotics"
BG = "#000008"
WIDTH, HEIGHT = 3440, 1440   # typical 34" ultrawide resolution

ACCENT1 = (0, 220, 255)    # cyan
ACCENT2 = (180, 0, 255)    # violet
ACCENT3 = (0, 255, 120)    # green

def rgb(r, g, b):
    r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
    return f"#{r:02x}{g:02x}{b:02x}"

def lerp(a, b, t):
    return a + (b - a) * t


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color")

    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, w, h):
        edge = random.randint(0, 3)
        if edge == 0:
            self.x, self.y = random.uniform(0, w), 0
        elif edge == 1:
            self.x, self.y = w, random.uniform(0, h)
        elif edge == 2:
            self.x, self.y = random.uniform(0, w), h
        else:
            self.x, self.y = 0, random.uniform(0, h)
        dx, dy = w / 2 - self.x, h / 2 - self.y
        dist = math.hypot(dx, dy) or 1
        speed = random.uniform(0.4, 1.8)
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        self.max_life = random.randint(120, 300)
        self.life = 0
        col_choice = random.choice([ACCENT1, ACCENT2, ACCENT3])
        self.color = col_choice

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy
        self.life += 1
        if self.life >= self.max_life:
            self.reset(w, h)

    def alpha_color(self):
        t = self.life / self.max_life
        bright = int(255 * (1 - abs(t * 2 - 1)))  # fade in/out
        r = int(self.color[0] * bright / 255)
        g = int(self.color[1] * bright / 255)
        b = int(self.color[2] * bright / 255)
        return rgb(r, g, b)


class App34:
    def __init__(self, root):
        self.root = root
        root.title("Rainbow Robotics — 34\"")
        root.configure(bg=BG)
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.tick = 0
        self.particles = [Particle(WIDTH, HEIGHT) for _ in range(220)]
        self.particle_dots = []

        self._build_grid()
        self._build_corner_huds()
        self._build_title()
        self._build_status_bars()
        self._init_particles()
        self._animate()

    def _build_grid(self):
        """Static perspective grid lines — futuristic floor grid."""
        vp_x, vp_y = WIDTH // 2, HEIGHT // 2 + 100
        grid_color = "#0a0a20"
        # horizontal lines
        for i in range(12):
            y = vp_y + 80 + i * 55
            if y > HEIGHT:
                break
            t = i / 12
            half_w = int(lerp(10, WIDTH // 2, t))
            self.canvas.create_line(
                vp_x - half_w, y, vp_x + half_w, y,
                fill=grid_color, width=1
            )
        # vertical lines converging to vp
        for i in range(-10, 11):
            end_x = vp_x + i * (WIDTH // 20)
            self.canvas.create_line(
                vp_x, vp_y, end_x, HEIGHT,
                fill=grid_color, width=1
            )

    def _build_corner_huds(self):
        """Decorative HUD corner brackets."""
        size = 60
        lw = 2
        color = rgb(*ACCENT1)
        pads = [(30, 30), (WIDTH - 30, 30), (30, HEIGHT - 30), (WIDTH - 30, HEIGHT - 30)]
        dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for (px, py), (dx, dy) in zip(pads, dirs):
            self.canvas.create_line(px, py, px + dx * size, py, fill=color, width=lw)
            self.canvas.create_line(px, py, px, py + dy * size, fill=color, width=lw)

        # inner ring decorations
        cx, cy = WIDTH // 2, HEIGHT // 2
        for r, col in [(340, ACCENT2), (400, ACCENT1)]:
            dim = tuple(c // 8 for c in col)
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=rgb(*dim), width=1, dash=(6, 10)
            )

    def _build_title(self):
        cx, cy = WIDTH // 2, HEIGHT // 2 - 80
        font_size = 160

        # shadow layers for 3-D depth
        for offset, alpha in [(8, 16), (5, 30), (2, 60)]:
            self.canvas.create_text(
                cx + offset, cy + offset,
                text=COMPANY,
                font=("Impact", font_size, "bold"),
                fill=rgb(0, alpha, alpha)
            )

        # main text — will be updated each frame
        self.title_main = self.canvas.create_text(
            cx, cy,
            text=COMPANY,
            font=("Impact", font_size, "bold"),
            fill=rgb(*ACCENT1)
        )

        # underline bar
        bar_w = 900
        self.underline = self.canvas.create_rectangle(
            cx - bar_w // 2, cy + 105,
            cx + bar_w // 2, cy + 110,
            fill=rgb(*ACCENT2), outline=""
        )

        # subtitle
        self.canvas.create_text(
            cx, cy + 140,
            text="A U T O M A T I O N  &  R O B O T I C S",
            font=("Courier New", 30, "bold"),
            fill=rgb(*tuple(c // 3 for c in ACCENT1))
        )

    def _build_status_bars(self):
        """Bottom HUD status indicators."""
        labels = ["SYSTEM", "NETWORK", "AI ENGINE", "SENSORS"]
        bar_w, bar_h = 260, 12
        gap = 80
        total = len(labels) * bar_w + (len(labels) - 1) * gap
        start_x = WIDTH // 2 - total // 2
        y = HEIGHT - 90

        self.status_bars = []
        for i, lbl in enumerate(labels):
            x = start_x + i * (bar_w + gap)
            self.canvas.create_text(
                x + bar_w // 2, y - 18,
                text=lbl, font=("Courier New", 14), fill=rgb(80, 80, 120)
            )
            bg_bar = self.canvas.create_rectangle(
                x, y, x + bar_w, y + bar_h,
                fill="#0a0a18", outline=rgb(30, 30, 60)
            )
            fg_bar = self.canvas.create_rectangle(
                x, y, x + 1, y + bar_h,
                fill=rgb(*ACCENT3), outline=""
            )
            self.status_bars.append((fg_bar, x, y, bar_w, bar_h, i))

    def _init_particles(self):
        for p in self.particles:
            dot = self.canvas.create_oval(0, 0, 2, 2, fill=rgb(*ACCENT1), outline="")
            self.particle_dots.append(dot)

    def _animate(self):
        self.tick += 1
        t = self.tick / 60.0

        # update title color — pulse between cyan and violet
        phase = (math.sin(t * 0.8) + 1) / 2
        tc = tuple(int(lerp(ACCENT1[i], ACCENT2[i], phase)) for i in range(3))
        self.canvas.itemconfig(self.title_main, fill=rgb(*tc))

        # glitch effect — occasional horizontal shift
        if self.tick % 90 < 3:
            shift = random.randint(-6, 6)
            cx = WIDTH // 2 + shift
            cy = HEIGHT // 2 - 80
            self.canvas.coords(self.title_main, cx, cy)
        else:
            self.canvas.coords(self.title_main, WIDTH // 2, HEIGHT // 2 - 80)

        # underline pulse width
        bar_phase = (math.sin(t * 1.2) + 1) / 2
        bar_w = int(600 + 400 * bar_phase)
        cx = WIDTH // 2
        cy = HEIGHT // 2 - 80
        self.canvas.coords(
            self.underline,
            cx - bar_w // 2, cy + 105,
            cx + bar_w // 2, cy + 110
        )
        ul_color = tuple(int(lerp(ACCENT2[i], ACCENT1[i], bar_phase)) for i in range(3))
        self.canvas.itemconfig(self.underline, fill=rgb(*ul_color))

        # update particles
        for i, (p, dot) in enumerate(zip(self.particles, self.particle_dots)):
            p.update(WIDTH, HEIGHT)
            x, y = p.x, p.y
            self.canvas.coords(dot, x - 1, y - 1, x + 1, y + 1)
            self.canvas.itemconfig(dot, fill=p.alpha_color())

        # animate status bars
        for fg_bar, x, y, bw, bh, idx in self.status_bars:
            fill = 0.5 + 0.5 * math.sin(t * (0.7 + idx * 0.3) + idx)
            end_x = x + int(bw * fill)
            self.canvas.coords(fg_bar, x, y, end_x, y + bh)
            c = (ACCENT1, ACCENT2, ACCENT3, ACCENT1)[idx]
            self.canvas.itemconfig(fg_bar, fill=rgb(*c))

        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    if sw < WIDTH or sh < HEIGHT:
        WIDTH, HEIGHT = sw, sh
    App34(root)
    root.mainloop()
