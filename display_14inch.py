"""
Rainbow Robotics — 14-inch Display
Animation: Bouncing neon letters that each drift independently
"""
import tkinter as tk
import math
import random

COMPANY = "Rainbow Robotics"
BG = "#0a0a0a"
NEON_COLORS = ["#ff0055", "#ff6600", "#ffdd00", "#00ff88", "#00cfff", "#aa44ff"]
WIDTH, HEIGHT = 1366, 768   # typical 14" laptop resolution

class Letter:
    def __init__(self, char, x, y, color, vx, vy, canvas, font_size=72):
        self.char = char
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.canvas = canvas
        self.font_size = font_size
        self.id = canvas.create_text(
            x, y, text=char,
            font=("Courier New", font_size, "bold"),
            fill=color
        )
        self.glow_id = canvas.create_text(
            x + 2, y + 2, text=char,
            font=("Courier New", font_size, "bold"),
            fill=self._dim(color)
        )
        canvas.tag_lower(self.glow_id, self.id)

    def _dim(self, hex_color):
        r = int(hex_color[1:3], 16) // 4
        g = int(hex_color[3:5], 16) // 4
        b = int(hex_color[5:7], 16) // 4
        return f"#{r:02x}{g:02x}{b:02x}"

    def update(self, w, h):
        self.x += self.vx
        self.y += self.vy
        half = self.font_size // 2
        if self.x < half or self.x > w - half:
            self.vx *= -1
            self.x = max(half, min(w - half, self.x))
        if self.y < half or self.y > h - half:
            self.vy *= -1
            self.y = max(half, min(h - half, self.y))
        self.canvas.coords(self.id, self.x, self.y)
        self.canvas.coords(self.glow_id, self.x + 2, self.y + 2)


class App14:
    def __init__(self, root):
        self.root = root
        root.title("Rainbow Robotics — 14\"")
        root.configure(bg=BG)
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self._draw_subtitle()
        self.letters = self._make_letters()
        self.tick = 0
        self._animate()

    def _draw_subtitle(self):
        self.canvas.create_text(
            WIDTH // 2, HEIGHT - 60,
            text="EXHIBITION 2026  •  14\"",
            font=("Courier New", 16),
            fill="#444444"
        )

    def _make_letters(self):
        chars = [c for c in COMPANY if c != " "]
        letters = []
        cx, cy = WIDTH // 2, HEIGHT // 2
        spread_x = 600
        spread_y = 200
        for i, ch in enumerate(chars):
            angle = (i / len(chars)) * 2 * math.pi
            x = cx + spread_x * 0.5 * math.cos(angle) * random.uniform(0.4, 1.0)
            y = cy + spread_y * math.sin(angle) * random.uniform(0.4, 1.0)
            color = NEON_COLORS[i % len(NEON_COLORS)]
            speed = random.uniform(1.5, 3.5)
            ang = random.uniform(0, 2 * math.pi)
            vx = speed * math.cos(ang)
            vy = speed * math.sin(ang)
            letters.append(Letter(ch, x, y, color, vx, vy, self.canvas, font_size=64))
        return letters

    def _animate(self):
        self.tick += 1
        for letter in self.letters:
            letter.update(WIDTH, HEIGHT)
        # pulse glow alpha via color brightness cycling
        if self.tick % 4 == 0:
            for i, letter in enumerate(self.letters):
                phase = (self.tick / 30 + i * 0.4) % (2 * math.pi)
                base = NEON_COLORS[i % len(NEON_COLORS)]
                r = int(int(base[1:3], 16) * (0.6 + 0.4 * math.sin(phase)))
                g = int(int(base[3:5], 16) * (0.6 + 0.4 * math.sin(phase)))
                b = int(int(base[5:7], 16) * (0.6 + 0.4 * math.sin(phase)))
                color = f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}"
                self.canvas.itemconfig(letter.id, fill=color)
        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    App14(root)
    root.mainloop()
