"""
Rainbow Robotics — Display 1
Animation: Continuous rainbow fireworks bursting across the screen
"""
import tkinter as tk
import math
import random

COMPANY = "Rainbow Robotics"
BG = "#000000"

PALETTE = [
    "#ff0044", "#ff4400", "#ffaa00", "#ffee00",
    "#00ff88", "#00ddff", "#0088ff", "#aa00ff", "#ff00cc",
]

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
        self.vy += 0.12   # gravity
        self.vx *= 0.97   # drag
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
        speed = random.uniform(8, 14)
        dist = self.ty - self.y
        self.vy = speed * (dist / abs(dist or 1)) * -1
        self.color = random.choice(PALETTE)
        self.exploded = False
        self.sparks = []

    def update(self, w, h):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.ty:
                self.exploded = True
                count = random.randint(80, 150)
                for _ in range(count):
                    self.sparks.append(Spark(self.x, self.y, self.color))
        else:
            self.sparks = [s for s in self.sparks if s.update()]
        return not self.exploded or len(self.sparks) > 0


class App:
    def __init__(self, root):
        self.root = root
        root.title("Rainbow Robotics")
        root.configure(bg=BG)
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda e: root.destroy())

        self.W = root.winfo_screenwidth()
        self.H = root.winfo_screenheight()

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.fireworks = []
        self.sparks_on_canvas = {}  # spark -> oval id
        self.trails = []

        self._draw_title()
        self.tick = 0
        self._animate()

    def _draw_title(self):
        cx = self.W // 2
        # glow shadow
        for off, col in [(6, "#330011"), (3, "#660022")]:
            self.canvas.create_text(cx + off, 70 + off, text=COMPANY,
                font=("Impact", 72, "bold"), fill=col)
        self.title_id = self.canvas.create_text(
            cx, 70, text=COMPANY,
            font=("Impact", 72, "bold"), fill="#ffffff"
        )
        # animated underline stored for later color update
        self.uline = self.canvas.create_rectangle(
            cx - 340, 115, cx + 340, 120,
            fill="#ff0044", outline=""
        )

    def _animate(self):
        self.tick += 1
        W, H = self.W, self.H

        # launch new fireworks
        if self.tick % 18 == 0 or len(self.fireworks) < 3:
            self.fireworks.append(Firework(W, H))

        # clear old spark ovals not in use
        active_sparks = set()
        new_fws = []
        for fw in self.fireworks:
            alive = fw.update(W, H)
            if alive:
                new_fws.append(fw)
                if fw.exploded:
                    for s in fw.sparks:
                        active_sparks.add(id(s))
        self.fireworks = new_fws

        # collect all sparks
        all_sparks = []
        for fw in self.fireworks:
            all_sparks.extend(fw.sparks)

        # delete stale canvas items
        stale = [sid for sid in self.sparks_on_canvas
                 if sid not in {id(s) for s in all_sparks}]
        for sid in stale:
            self.canvas.delete(self.sparks_on_canvas.pop(sid))

        # draw / update sparks
        for s in all_sparks:
            col = s.alpha_color()
            sz = s.size
            sid = id(s)
            if sid in self.sparks_on_canvas:
                oid = self.sparks_on_canvas[sid]
                self.canvas.coords(oid, s.x - sz, s.y - sz, s.x + sz, s.y + sz)
                self.canvas.itemconfig(oid, fill=col)
            else:
                oid = self.canvas.create_oval(
                    s.x - sz, s.y - sz, s.x + sz, s.y + sz,
                    fill=col, outline=""
                )
                self.sparks_on_canvas[sid] = oid

        # draw rising shells as small dots
        for fw in self.fireworks:
            if not fw.exploded:
                self.canvas.create_oval(
                    fw.x - 2, fw.y - 2, fw.x + 2, fw.y + 2,
                    fill=fw.color, outline=""
                )

        # pulse title color and underline
        phase = (self.tick / 40) % 1.0
        n = len(PALETTE)
        idx = int(phase * n)
        self.canvas.itemconfig(self.title_id, fill=PALETTE[idx % n])
        self.canvas.itemconfig(self.uline, fill=PALETTE[(idx + 3) % n])

        # keep title on top
        self.canvas.tag_raise(self.title_id)
        self.canvas.tag_raise(self.uline)

        self.root.after(16, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
