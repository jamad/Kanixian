import pyxel, math

APP_WIDTH, APP_HEIGHT = 480, 640
CHAR_SIZE = 16

class Squad:
    def __init__(self):
        self.x, self.y = CHAR_SIZE * 6, CHAR_SIZE * 4
        self.list = [[Teki(x*10, i*20, i, self.x, self.y) for x in R] for i, R in enumerate([(10, 20), range(2, 30, 2)] + [range(0, 32, 2)]*5)]
        self.dx = 0.2                                                           # horizontal move speed

    def update(self):
        self.x += self.dx                                                       # horizontal move
        if not (CHAR_SIZE <= self.x <= CHAR_SIZE * 9):self.dx *= -1             # horizontal direction change
        self.y += math.sin(pyxel.frame_count / 180 * math.pi) * 0.25            # vertical move

        if pyxel.frame_count % 15 == 0:                                         # flying phase
            enemies = [enemy for row in self.list for enemy in row if enemy]    
            chosen = enemies[pyxel.rndi(0, len(enemies) - 1)]
            chosen.is_flying = True
            chosen.dx = (-1, 1)[pyxel.rndi(0, 1)]                               # random direction
            chosen.fly()

class Teki:
    def __init__(self, rx, ry, num, squad_x,squad_y):
        self.rposx, self.rposy = rx, ry
        self.num = min(3, num)
        self.cnt = self.is_flying = self.is_return = 0
        self.x, self.y = squad_x + self.rposx, squad_y + self.rposy
        self.dx, self.dy, self.trajectory = 0, 0, []

    def move(self, tx, ty):
        vx, vy = tx - self.x, ty - self.y
        dist = math.sqrt(vx * vx + vy * vy)
        self.dx, self.dy = (vx, vy) if dist < 1 else (vx / dist * 2, vy / dist * 2)
        self.x += self.dx
        self.y += self.dy
        return dist < 1

    def update(self):
        self.cnt += 1
        if self.is_return:
            if self.move(App.enemy_group.x + self.rposx, App.enemy_group.y + self.rposy): # move and if it reached the destination
                self.is_flying = self.is_return = 0
        elif self.is_flying:
            if self.trajectory and self.move(*self.trajectory[-1]):                       # if arrived at destination, next destination
                self.trajectory.pop()
            if self.y > APP_HEIGHT + 32:
                self.is_return, self.y, self.x = True, -CHAR_SIZE * 2, APP_WIDTH / 2      # teleporting
        else:
            self.x, self.y = App.enemy_group.x + self.rposx, App.enemy_group.y + self.rposy

    def draw(self):
        u = 2 + (0 < self.dx) if self.is_flying else (self.cnt // 30) % 2
        pyxel.blt(self.x, self.y, 0, u * CHAR_SIZE, (self.num + 3) * CHAR_SIZE, CHAR_SIZE, CHAR_SIZE, 0)

    def fly(self):
        self.is_flying = True
        px,py=self.x + 50, self.y + 1000
        self.trajectory =  [
            [
            (1 - t) ** 3 * self.x + 3 * (1 - t) ** 2 * t * (px / 2) + 3 * (1 - t) * t ** 2 * px + t ** 3 * (APP_WIDTH / 2),
            (1 - t) ** 3 * self.y + 3 * (1 - t) ** 2 * t * (py / 2) + 3 * (1 - t) * t ** 2 * py + t ** 3 * (APP_HEIGHT + 64)
            ] for i in range(10) for t in [(i + 1) / 11]]
        self.trajectory.reverse()
        self.dy = -1

class App:
    enemy_group = Squad()
    
    def __init__(self):
        pyxel.init(APP_WIDTH, APP_HEIGHT, title="Kanixian MOD", fps=120)
        pyxel.load("kani.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        App.enemy_group.update()
        [teki.update()for row in App.enemy_group.list for teki in row]
                
    def draw(self):
        pyxel.cls(0)
        [teki.draw()for row in App.enemy_group.list for teki in row]
                
App()