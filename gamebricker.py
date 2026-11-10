import tkinter as tk
import random
import threading

try:
    import winsound
except ImportError:
    winsound = None


# =====================================
# GAME OBJECT CLASS
# =====================================

class GameObject:

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# =====================================
# PARTICLE CLASS
# =====================================

class Particle:

    def __init__(self, canvas, x, y, color):

        self.canvas = canvas

        self.x = x
        self.y = y

        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(-4, 4)

        self.life = 25

        self.item = canvas.create_oval(
            x, y, x + 5, y + 5,
            fill=color,
            outline=""
        )

    def update(self):

        self.x += self.speed_x
        self.y += self.speed_y

        self.life -= 1

        self.canvas.coords(
            self.item,
            self.x,
            self.y,
            self.x + 5,
            self.y + 5
        )

        if self.life <= 0:

            self.canvas.delete(self.item)
            return False

        return True


# =====================================
# BALL CLASS
# =====================================

class Ball(GameObject):

    def __init__(self, canvas, x, y):

        self.radius = 9

        self.speed_x = 5
        self.speed_y = -5

        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="#00ffff",
            outline="white",
            width=2
        )

        super().__init__(canvas, item)

    def update(self):

        coords = self.get_position()

        width = self.canvas.winfo_width()

        # Collision dinding kiri dan kanan
        if coords[0] <= 0:
            self.speed_x = abs(self.speed_x)

        elif coords[2] >= width:
            self.speed_x = -abs(self.speed_x)

        # Collision dinding atas
        if coords[1] <= 60:
            self.speed_y = abs(self.speed_y)

        self.move(
            self.speed_x,
            self.speed_y
        )

    def reverse_y(self):
        self.speed_y *= -1

    def reverse_x(self):
        self.speed_x *= -1


