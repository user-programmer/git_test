"""
Rainbow Robotics — 27-inch Display
Animation: Full-screen rainbow wave sweeping across the title + rotating
           geometric rings in the background
"""
import tkinter as tk
import math

COMPANY = "Rainbow Robotics"
BG = "#050510"
WIDTH, HEIGHT = 2560, 1440   # typical 27" QHD resolution (falls back gracefully)

RAINBOW = [
    (255, 0,   80),
    (255, 100, 0),
    (255, 220, 0),
    (0,   220, 80),
    (0,   180, 255),
    (140, 0,   255),
]

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def rgb(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def rainbow_at(t):
    t = t % 1.0
    n = len(RAINBOW)
    idx = int(t * n)
    frac = (t * n) - idx
    return lerp_color(RAINBOW[idx % n], RAINBOW[(idx + 1) % n], frac)


class App27:
    def __init__(self, root):
        self.root = root
        root.title("Rainbow Robotics — 27\"")
        root.configure(bg=BG)
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.tick = 0
        self.rings = []
        self.letter_ids = []
        self.char_xs = []

        self._build_rings()
        self._build_title()
        self._build_tagline()
        self._animate()

    def _build_rings(self):
        cx, cy = WIDTH // 2, HEIGHT // 2
        for i in range(8):
            r = 80 + i * 90
            ring = self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline="#1a1a3a", width=2
            )
            self.rings.append((ring, r, i))

    def _build_title(self):
        font_size = 130
        cx = WIDTH // 2
        cy = HEIGHT // 2 - 60
        # measure spacing by creating hidden temp; just space evenly
        chars = list(COMPANY)
        n = len(chars)
        char_w = font_size * 0.62          # approx char width
        total = n * char_w
        start_x = cx - total / 2 + char_w / 2
        self.letter_ids = []
        self.char_xs = []
        for i, ch in enumerate(chars):
            x = start_x + i * char_w
            glow = self.canvas.create_text(
                x + 3, cy + 3, text=ch,
                font=("Impact", font_size, "bold"),
                fill="#000030"
            )
            lid = self.canvas.create_text(
                x, cy, text=ch,
                font=("Impact", font_size, "bold"),
                fill="#ffffff"
            )
            self.letter_ids.append((lid, glow, i))
            self.char_xs.append(x)

    def _build_tagline(self):
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 120,
            text="INNOVATION  •  AUTOMATION  •  INTELLIGENCE",
            font=("Helvetica", 28, "bold"),
            fill="#333355"
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT - 60,
            text="EXHIBITION 2026  •  27\"",
            font=("Helvetica", 20),
            fill="#222244"
        )

    def _animate(self):
        self.tick += 1
        t = self.tick / 60.0

        # rotate rings
        cx, cy = WIDTH // 2, HEIGHT // 2
        for ring_id, r, i in self.rings:
            angle = t * (0.3 + i * 0.07) * (1 if i % 2 == 0 else -1)
            # rings stay circular — shift their color
            phase = (i / 8 + t * 0.1) % 1.0
            rc = rainbow_at(phase)
            dim = tuple(c // 6 for c in rc)
            self.canvas.itemconfig(ring_id, outline=rgb(*dim))

        # draw scanline across rings (decorative dash)
        if hasattr(self, "_scan"):
            self.canvas.delete(self._scan)
        scan_y = HEIGHT // 2 + int(200 * math.sin(t * 0.7))
        self._scan = self.canvas.create_line(
            cx - 700, scan_y, cx + 700, scan_y,
            fill=rgb(*tuple(c // 5 for c in rainbow_at(t * 0.05 % 1))),
            width=1, dash=(4, 8)
        )

        # rainbow wave across letters
        for lid, glow, i in self.letter_ids:
            wave_phase = (i / len(self.letter_ids) - t * 0.25) % 1.0
            r, g, b = rainbow_at(wave_phase)
            self.canvas.itemconfig(lid, fill=rgb(r, g, b))
            # gentle vertical bob
            bob = int(12 * math.sin(t * 1.5 + i * 0.35))
            base_y = HEIGHT // 2 - 60
            self.canvas.coords(lid, self.char_xs[i], base_y + bob)
            self.canvas.coords(glow, self.char_xs[i] + 3, base_y + bob + 3)

        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    # auto-fit if screen is smaller
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    if sw < WIDTH or sh < HEIGHT:
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = sw, sh
    App27(root)
    root.mainloop()
