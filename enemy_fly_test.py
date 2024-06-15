import pyxel, math

APP_WIDTH, APP_HEIGHT = 480, 640
CHAR_SIZE = 16

class Squad:
    def __init__(self):
        self.dx = 0.2                                                           # horizontal move speed
        self.x, self.y = CHAR_SIZE * 6, CHAR_SIZE * 4
        self.list = [[Enemy(x*10, i*20, i, self.x, self.y) for x in R] for i, R in enumerate([(10, 20), range(2, 30, 2)] + [range(0, 32, 2)]*5)]

        self.playerx=APP_WIDTH/2
        self.playery=APP_HEIGHT/2

    def update(self):
        self.x += self.dx                                                       # horizontal move
        if not (CHAR_SIZE <= self.x <= CHAR_SIZE * 9):self.dx *= -1             # horizontal direction change
        self.y += math.sin(pyxel.frame_count / 180 * math.pi) * 0.25            # vertical move

        if pyxel.frame_count % 15 == 0:                                         # flying phase
            enemies = [enemy for row in self.list for enemy in row if enemy]    
            chosen = enemies[pyxel.rndi(0, len(enemies) - 1)]
            chosen.is_flying = True
            chosen.dx = (-1, 1)[pyxel.rndi(0, 1)]                               # random direction
            px,py=chosen.x + self.playerx, chosen.y + self.playery
            chosen.trajectory =  [
                [
                (1 - t) ** 3 * chosen.x + 3 * (1 - t) ** 2 * t * (px / 2) + 3 * (1 - t) * t ** 2 * px + t ** 3 * (APP_WIDTH / 2),
                (1 - t) ** 3 * chosen.y + 3 * (1 - t) ** 2 * t * (py / 2) + 3 * (1 - t) * t ** 2 * py + t ** 3 * (APP_HEIGHT + 64)
                ] for i in range(9,-1,-1) for t in [(i + 1) / 11]]
            chosen.dy = -1

        [enemy.update(self.x,self.y)for row in self.list for enemy in row]

        # player update

    
    def draw(self):
        [enemy.draw()for row in self.list for enemy in row]

        pyxel.circ(self.playerx,self.playery,3,7)

class Enemy:
    def __init__(self, rx, ry, num, squad_x,squad_y):
        self.home_x, self.home_y = rx, ry
        self.num = min(3, num)
        self.anim_pattern = self.is_flying = self.is_return = 0
        self.x, self.y = squad_x + self.home_x, squad_y + self.home_y
        self.dx, self.dy, self.trajectory = 0, 0, []

    def move(self, tx, ty): # goes to (tx,ty)
        vx, vy = tx - self.x, ty - self.y                                               # vector 
        dist = math.sqrt(vx * vx + vy * vy)                                             # distance
        arrived= dist < 1                                                               # true if arrived at destination
        self.dx, self.dy = (vx, vy) if arrived else (2*vx /dist, 2*vy/dist)             # delta unit vector x2
        self.x += self.dx                                                               # posx update
        self.y += self.dy                                                               # posy update
        return arrived                                                                 

    def update(self,squad_x,squad_y):
        self.anim_pattern += 1 # pattern animation
        x=squad_x + self.home_x
        y=squad_y + self.home_y
        if self.is_return:
            if self.move(x, y): # move and if it reached the destination
                self.is_flying = self.is_return = 0
        elif self.is_flying:
            if self.trajectory and self.move(*self.trajectory[-1]):                       # if arrived at destination, next destination
                self.trajectory.pop()   # trajectory is changed as stack
            if self.y > APP_HEIGHT + 32:
                self.is_return, self.y, self.x = True, -CHAR_SIZE * 2, APP_WIDTH / 2      # teleporting
        else:
            self.x, self.y = x, y

    def draw(self):
        u = 2 + (0 < self.dx) if self.is_flying else (self.anim_pattern // 30) % 2
        pyxel.blt(self.x, self.y, 0, u * CHAR_SIZE, (self.num + 3) * CHAR_SIZE, CHAR_SIZE, CHAR_SIZE, 0)

        # debug display
        if self.is_flying: 
            pyxel.text(self.x, self.y + 16, f'{int(self.x)},{int(self.y)}', 7)
            for p1, p2 in zip(self.trajectory, self.trajectory[1:]):
                pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)
                pyxel.circ(p2[0], p2[1], 2,7)

class App:
    def __init__(self):
        pyxel.init(APP_WIDTH, APP_HEIGHT, title="Kanixian MOD", fps=120)
        pyxel.load("kani.pyxres")
        self.squad = Squad()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.squad.update()
                
    def draw(self):
        pyxel.cls(0)
        self.squad.draw()
                
App()