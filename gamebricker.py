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


# =====================================
# PADDLE CLASS
# =====================================

class Paddle(GameObject):

    def __init__(self, canvas, x, y):

        self.width = 110
        self.height = 15
        self.speed = 9

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="#00ff99",
            outline="white",
            width=2
        )

        super().__init__(canvas, item)

    def move_paddle(self, direction):

        coords = self.get_position()

        width = self.canvas.winfo_width()

        offset = direction * self.speed

        if (
            coords[0] + offset >= 0
            and coords[2] + offset <= width
        ):

            self.move(offset, 0)


# =====================================
# BRICK CLASS
# =====================================

class Brick(GameObject):

    COLORS = {
        1: "#ff4757",
        2: "#ffa502",
        3: "#2ed573"
    }

    def __init__(self, canvas, x, y, hits):

        self.width = 70
        self.height = 22

        self.hits = hits

        item = canvas.create_rectangle(
            x,
            y,
            x + self.width,
            y + self.height,
            fill=self.COLORS[hits],
            outline="white",
            width=1
        )

        super().__init__(canvas, item)

    def hit(self):

        self.hits -= 1

        if self.hits <= 0:

            self.delete()
            return True

        self.canvas.itemconfig(
            self.item,
            fill=self.COLORS[self.hits]
        )

        return False


# =====================================
# MAIN GAME CLASS
# =====================================

class Game(tk.Frame):

    def __init__(self, master):

        super().__init__(master)

        self.width = 800
        self.height = 600

        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0

        self.running = False
        self.paused = False
        self.game_over = False

        self.keys = set()

        self.particles = []
        self.ball_trail = []
        self.stars = []

        self.message = None
        self.flash = 0

        # Canvas
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#101820",
            highlightthickness=0
        )

        self.canvas.pack()
        self.pack()

        # Game objects
        self.ball = None
        self.paddle = None
        self.bricks = []

        # Background
        self.create_background()

        # HUD
        self.create_hud()

        # Create game objects
        self.create_paddle()
        self.create_bricks()
        self.create_ball()

        # Instructions
        self.show_message(
            "PRESS SPACE TO START",
            "#ffffff",
            24,
            300
        )

        self.canvas.create_text(
            400,
            335,
            text="Use LEFT / RIGHT or A / D to move",
            fill="#aaaaaa",
            font=("Arial", 12)
        )

        # Keyboard
        self.canvas.focus_set()

        self.canvas.bind(
            "<KeyPress>",
            self.key_press
        )

        self.canvas.bind(
            "<KeyRelease>",
            self.key_release
        )

        # Game loop
        self.after(16, self.game_loop)

    # =====================================
    # BACKGROUND
    # =====================================

    def create_background(self):

        self.stars = []

        for i in range(50):

            x = random.randint(0, self.width)
            y = random.randint(60, self.height)

            star = self.canvas.create_oval(
                x,
                y,
                x + 2,
                y + 2,
                fill="white",
                outline=""
            )

            self.stars.append(star)

    def update_background(self):

        for star in self.stars:

            self.canvas.move(star, 0, 0.5)

            coords = self.canvas.coords(star)

            if coords[1] >= self.height:

                x = random.randint(0, self.width)

                self.canvas.coords(
                    star,
                    x, 60,
                    x + 2, 62
                )

    # =====================================
    # HUD
    # =====================================

    def create_hud(self):

        self.canvas.create_rectangle(
            0, 0,
            self.width, 60,
            fill="#202b38",
            outline=""
        )

        self.score_text = self.canvas.create_text(
            100, 30,
            text="SCORE: 0",
            fill="#00ffff",
            font=("Arial", 15, "bold")
        )

        self.lives_text = self.canvas.create_text(
            400, 30,
            text="LIVES: 3",
            fill="#ff4757",
            font=("Arial", 15, "bold")
        )

        self.level_text = self.canvas.create_text(
            690, 30,
            text="LEVEL: 1",
            fill="#2ed573",
            font=("Arial", 15, "bold")
        )

        self.combo_text = self.canvas.create_text(
            400, 80,
            text="",
            fill="#ffa502",
            font=("Arial", 14, "bold")
        )

    def update_hud(self):

        self.canvas.itemconfig(
            self.score_text,
            text=f"SCORE: {self.score}"
        )

        self.canvas.itemconfig(
            self.lives_text,
            text=f"LIVES: {self.lives}"
        )

        self.canvas.itemconfig(
            self.level_text,
            text=f"LEVEL: {self.level}"
        )

        if self.combo >= 2:

            self.canvas.itemconfig(
                self.combo_text,
                text=f"COMBO x{self.combo}!"
            )

        else:

            self.canvas.itemconfig(
                self.combo_text,
                text=""
            )

    # =====================================
    # CREATE PADDLE
    # =====================================

    def create_paddle(self):

        self.paddle = Paddle(
            self.canvas,
            self.width / 2,
            550
        )

    # =====================================
    # CREATE BALL
    # =====================================

    def create_ball(self):

        if self.ball is not None:

            self.ball.delete()

        coords = self.paddle.get_position()

        x = (coords[0] + coords[2]) / 2

        self.ball = Ball(
            self.canvas,
            x,
            530
        )

    # =====================================
    # CREATE BRICKS
    # =====================================

    def create_bricks(self):

        self.bricks = []

        rows = 5
        columns = 9

        brick_width = 70
        gap = 10

        start_x = 45
        start_y = 100

        for row in range(rows):

            for col in range(columns):

                x = start_x + col * (brick_width + gap)

                y = start_y + row * 32

                hits = ((row + self.level - 1) % 3) + 1

                brick = Brick(
                    self.canvas,
                    x,
                    y,
                    hits
                )

                self.bricks.append(brick)

    # =====================================
    # MESSAGE
    # =====================================

    def show_message(self, text, color, size, y):

        self.message = self.canvas.create_text(
            self.width / 2,
            y,
            text=text,
            fill=color,
            font=("Arial", size, "bold")
        )

    def clear_message(self):

        if self.message is not None:

            self.canvas.delete(self.message)

            self.message = None

    # =====================================
    # SOUND EFFECT
    # =====================================

    def play_sound(self, sound_type):

        if winsound is None:
            return

        sounds = {
            "hit": (600, 50),
            "brick": (900, 100),
            "destroy": (1200, 150),
            "level": (1500, 300),
            "gameover": (300, 500)
        }

        frequency, duration = sounds[sound_type]

        def play():

            try:

                winsound.Beep(
                    frequency,
                    duration
                )

            except RuntimeError:
                pass

        threading.Thread(
            target=play,
            daemon=True
        ).start()

    # =====================================
    # PARTICLE EXPLOSION
    # =====================================

    def create_explosion(self, x, y, color):

        for i in range(15):

            particle = Particle(
                self.canvas,
                x,
                y,
                color
            )

            self.particles.append(particle)

        self.flash = 3

    def update_particles(self):

        for particle in self.particles[:]:

            alive = particle.update()

            if not alive:

                self.particles.remove(particle)

    # =====================================
    # BALL TRAIL EFFECT
    # =====================================

    def update_ball_trail(self):

        if not self.running or self.paused:
            return

        coords = self.ball.get_position()

        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2

        trail = self.canvas.create_oval(
            x - 4,
            y - 4,
            x + 4,
            y + 4,
            fill="#176b87",
            outline=""
        )

        self.ball_trail.append(trail)

        if len(self.ball_trail) > 8:

            old = self.ball_trail.pop(0)

            self.canvas.delete(old)

    def clear_ball_trail(self):

        for trail in self.ball_trail:

            self.canvas.delete(trail)

        self.ball_trail = []

    # =====================================
    # SCREEN FLASH
    # =====================================

    def update_flash(self):

        if self.flash > 0:

            self.flash -= 1

            if self.flash == 0:

                self.canvas.delete("flash")

    def create_flash(self):

        self.canvas.create_rectangle(
            0, 60,
            self.width, self.height,
            fill="white",
            stipple="gray50",
            outline="",
            tags="flash"
        )

        self.flash = 3

    # =====================================
    # KEYBOARD CONTROL
    # =====================================

    def key_press(self, event):

        key = event.keysym.lower()

        self.keys.add(key)

        if key == "space":

            if not self.running and not self.game_over:

                self.clear_message()

                self.running = True
                self.paused = False

            elif self.paused:

                self.paused = False

                self.clear_message()

        elif key == "p":

            if self.running:

                self.paused = True

                self.show_message(
                    "PAUSED - PRESS SPACE",
                    "#ffa502",
                    25,
                    300
                )

            elif self.paused:

                self.paused = False

                self.clear_message()

        elif key == "r":

            self.restart_game()

    def key_release(self, event):

        key = event.keysym.lower()

        self.keys.discard(key)

    # =====================================
    # COLLISION DETECTION
    # =====================================

    def check_collisions(self):

        ball_coords = self.ball.get_position()

        # Paddle collision
        paddle_coords = self.paddle.get_position()

        if (
            ball_coords[2] >= paddle_coords[0]
            and ball_coords[0] <= paddle_coords[2]
            and ball_coords[3] >= paddle_coords[1]
            and ball_coords[1] <= paddle_coords[3]
            and self.ball.speed_y > 0
        ):

            self.ball.speed_y = -abs(self.ball.speed_y)

            ball_center = (
                ball_coords[0] + ball_coords[2]
            ) / 2

            paddle_center = (
                paddle_coords[0] + paddle_coords[2]
            ) / 2

            self.ball.speed_x = (
                ball_center - paddle_center
            ) / 10

            self.combo = 0

            self.update_hud()

            self.play_sound("hit")

        # Brick collision
        for brick in self.bricks[:]:

            brick_coords = brick.get_position()

            if (
                ball_coords[2] >= brick_coords[0]
                and ball_coords[0] <= brick_coords[2]
                and ball_coords[3] >= brick_coords[1]
                and ball_coords[1] <= brick_coords[3]
            ):

                self.ball.reverse_y()

                color = Brick.COLORS[brick.hits]

                x = (
                    brick_coords[0] + brick_coords[2]
                ) / 2

                y = (
                    brick_coords[1] + brick_coords[3]
                ) / 2

                destroyed = brick.hit()

                self.create_explosion(
                    x, y, color
                )

                if destroyed:

                    self.score += 10

                    self.combo += 1

                    self.play_sound("destroy")

                    self.bricks.remove(brick)

                else:

                    self.score += 2

                    self.play_sound("brick")

                self.update_hud()

                break

    # =====================================
    # BALL LOST
    # =====================================

    def lose_life(self):

        self.lives -= 1

        self.update_hud()

        self.clear_ball_trail()

        self.play_sound("hit")

        if self.lives <= 0:

            self.show_game_over()

        else:

            self.create_ball()

            self.running = False

            self.show_message(
                "BALL LOST! PRESS SPACE",
                "#ffa502",
                22,
                300
            )

    # =====================================
    # GAME OVER
    # =====================================

    def show_game_over(self):

        self.running = False
        self.paused = False
        self.game_over = True

        self.play_sound("gameover")

        self.canvas.create_rectangle(
            150, 220,
            650, 390,
            fill="#202b38",
            outline="#ff4757",
            width=3
        )

        self.canvas.create_text(
            400, 270,
            text="GAME OVER",
            fill="#ff4757",
            font=("Arial", 32, "bold")
        )

        self.canvas.create_text(
            400, 320,
            text=f"FINAL SCORE: {self.score}",
            fill="white",
            font=("Arial", 18)
        )

        self.canvas.create_text(
            400, 355,
            text="PRESS R TO RESTART",
            fill="#00ffff",
            font=("Arial", 13, "bold")
        )

    # =====================================
    # NEXT LEVEL
    # =====================================

    def next_level(self):

        self.running = False

        self.level += 1

        self.play_sound("level")

        self.canvas.delete("all")

        self.particles = []
        self.ball_trail = []
        self.stars = []
        self.flash = 0

        self.create_background()

        self.create_hud()

        self.create_paddle()

        self.create_bricks()

        self.create_ball()

        self.update_hud()

        self.show_message(
            f"LEVEL {self.level} COMPLETED!",
            "#2ed573",
            28,
            300
        )

        self.after(1500, self.start_next_level)

    def start_next_level(self):

        if not self.game_over:

            self.clear_message()

            self.running = True

    # =====================================
    # START GAME
    # =====================================

    def start_game(self):

        self.clear_message()

        self.running = True

        self.paused = False

    # =====================================
    # RESTART GAME
    # =====================================

    def restart_game(self):

        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0

        self.running = False
        self.paused = False
        self.game_over = False

        self.keys.clear()

        self.particles = []
        self.ball_trail = []
        self.stars = []

        self.flash = 0

        self.canvas.delete("all")

        self.create_background()

        self.create_hud()

        self.create_paddle()

        self.create_bricks()

        self.create_ball()

        self.update_hud()

        self.show_message(
            "PRESS SPACE TO START",
            "#ffffff",
            24,
            300
        )

        self.canvas.create_text(
            400, 335,
            text="Use LEFT / RIGHT or A / D to move",
            fill="#aaaaaa",
            font=("Arial", 12)
        )

        self.canvas.focus_set()

    # =====================================
    # MAIN GAME LOOP
    # =====================================

    def game_loop(self):

        # Background animation
        self.update_background()

        # Particle animation
        self.update_particles()

        # Flash animation
        self.update_flash()

        if self.running and not self.paused:

            # Paddle movement
            if "left" in self.keys or "a" in self.keys:

                self.paddle.move_paddle(-1)

            if "right" in self.keys or "d" in self.keys:

                self.paddle.move_paddle(1)

            # Ball movement
            self.ball.update()

            # Ball trail
            self.update_ball_trail()

            # Collision
            self.check_collisions()

            # Check remaining bricks
            if len(self.bricks) == 0:

                self.next_level()

            # Check ball position
            elif self.ball.get_position()[3] >= self.height:

                self.lose_life()

        # Repeat game loop
        self.after(16, self.game_loop)


# =====================================
# MAIN PROGRAM
# =====================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title("BRICK BREAKER - ARCADE GAME")

    root.resizable(False, False)

    game = Game(root)

    root.mainloop()