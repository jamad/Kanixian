import pyxel, math

# Global Constants
APP_WIDTH = 480
APP_HEIGHT = 640
CHAR_SIZE = 16

# Global Variables
debugdisp = 0

class Squad:
    def __init__(self):
        self.x, self.y = CHAR_SIZE * 6, CHAR_SIZE * 4
        self.dx = 0.2
        self.list = [[], [], [], []]  # enemy arrays

    def update(self):
        self.x += self.dx  # horizontal group move
        theta = pyxel.frame_count / 180 * math.pi
        self.y += math.sin(theta) * 0.25
        if not (CHAR_SIZE <= self.x <= CHAR_SIZE * 9):
            self.dx *= -1  # reverse direction

        # Determine whether to start moving
        attack_interval = 15  # 0.25 sec each
        if pyxel.frame_count % attack_interval == 0:
            enemy_alive = [enemy for row in self.list for enemy in row]
            if enemy_alive:
                chosen = enemy_alive[pyxel.rndi(0, len(enemy_alive) - 1)]  # choose at random
                chosen.is_flying = True
                chosen.dx = (-1, 1)[pyxel.rndi(0, 1)]
                chosen.fly()

enemy_group = Squad()

class Teki:
    def __init__(self, rx, ry, num):
        self.rposx = rx
        self.rposy = ry
        self.num = min(3, num)
        self.cnt = 0  # Initialize animation counter
        self.is_flying = False
        self.is_return = False
        self.x = enemy_group.x + self.rposx
        self.y = enemy_group.y + self.rposy
        self.dx = 0
        self.dy = 0
        self.trajectory = []

    def move(self, tx, ty):
        vx = tx - self.x
        vy = ty - self.y
        dist = math.sqrt(vx * vx + vy * vy)
        if dist < 1:
            self.dx = vx
            self.dy = vy
        else:
            self.dx = vx / dist * 2
            self.dy = vy / dist * 2
        self.x += self.dx
        self.y += self.dy
        return dist < 1

    def update(self):
        self.cnt += 1
        if self.is_return:
            tx = enemy_group.x + self.rposx
            ty = enemy_group.y + self.rposy
            if self.move(tx, ty):
                self.is_flying = False
                self.is_return = False
        elif self.is_flying:
            if self.trajectory:
                tx, ty = self.trajectory[0]
                if self.move(tx, ty):
                    self.trajectory.pop(0)
                if APP_HEIGHT + 32 < self.y:
                    self.is_return = True
                    self.y = -CHAR_SIZE * 2
                    self.x = APP_WIDTH / 2
        else:
            self.x = enemy_group.x + self.rposx
            self.y = enemy_group.y + self.rposy

    def draw(self):
        u = 2 + (0 < self.dx) if self.is_flying else (self.cnt // 30) % 2
        v = self.num + 3
        pyxel.blt(self.x, self.y, 0, u * 16, v * 16, 16, 16, 0)

        if debugdisp and self.is_flying:
            pyxel.text(self.x, self.y + 16, f'{int(self.x)},{int(self.y)}', 7)
            for p1, p2 in zip(self.trajectory, self.trajectory[1:]):
                pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)

    def fly(self):
        self.is_flying = True
        px = self.x + 50
        py = self.y + 1000
        self.trajectory = self.generate_smooth_trajectory(px, py)
        self.dy = -1

    def generate_smooth_trajectory(self, px, py):
        trajectory = []
        num_points = 10  # Number of points for interpolation
        for i in range(num_points):
            t = (i + 1) / (num_points + 1)
            tx = (1 - t) ** 3 * self.x + 3 * (1 - t) ** 2 * t * (px / 2) + 3 * (1 - t) * t ** 2 * px + t ** 3 * (APP_WIDTH / 2)
            ty = (1 - t) ** 3 * self.y + 3 * (1 - t) ** 2 * t * (py / 2) + 3 * (1 - t) * t ** 2 * py + t ** 3 * (APP_HEIGHT + 64)
            trajectory.append([tx, ty])
        return trajectory

    def check_hit(self, shipx, shipy):
        return abs(shipx - self.x) < 12 and abs(shipy - self.y) < 12

class App:
    score = 0
    stage_number = 0
    message_list = []
    bullet_list = []
    tekibullets = []

    def __init__(self):
        pyxel.init(APP_WIDTH, APP_HEIGHT, title="Kanixian MOD", fps=120, display_scale=1)
        pyxel.load("kani.pyxres")
        pyxel.run(self.update, self.draw)

    def init_stage(self):
        App.bullet_list = []
        App.tekibullets = []
        App.stage_number += 1
        MAX_COL_NUM = 16 * 2
        enemy_group.list = [[Teki(x * 10, i * 20, i) for x in R] for i, R in enumerate([(4 + 3 * 2, 10 + 5 * 2), range(2, MAX_COL_NUM - 2, 2)] + [range(0, MAX_COL_NUM, 2)] * 5)]

    def update(self):
        if sum(map(len, enemy_group.list)) == 0:
            self.init_stage()
            return

        App.bullet_list = [bullet for bullet in App.bullet_list if bullet.y >= -10]
        App.tekibullets = [bullet for bullet in App.tekibullets if bullet.y <= APP_HEIGHT + 10]

        for bullet in App.bullet_list + App.tekibullets:
            bullet.update()
        enemy_group.update()
        for tekis in enemy_group.list:
            for teki in tekis:
                teki.update()

    def draw(self):
        pyxel.cls(0)
        for tekis in enemy_group.list:
            for teki in tekis:
                teki.draw()
        for bullet in App.bullet_list + App.tekibullets:
            bullet.draw()

App()
