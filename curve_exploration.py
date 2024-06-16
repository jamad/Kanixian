import pyxel, math

APP_WIDTH, APP_HEIGHT = 480, 640
CHAR_SIZE = 16

def playercontrol(): # my function to return player's movement
    move_R=pyxel.btn(pyxel.KEY_RIGHT)   or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
    move_L=pyxel.btn(pyxel.KEY_LEFT)    or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
    move_D=pyxel.btn(pyxel.KEY_DOWN)    or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
    move_U=pyxel.btn(pyxel.KEY_UP)      or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)

    player_dx=move_R or -move_L # 1 or -1 or 0
    player_dy=move_D or -move_U # 1 or -1 or 0
    return (player_dx,player_dy )

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

        if pyxel.frame_count % 120 == 0:                                         # flying phase
            enemies = [enemy for row in self.list for enemy in row if enemy]    
            chosen = enemies[pyxel.rndi(0, len(enemies) - 1)]
            chosen.is_flying = True
            chosen.dx = (-1, 1)[pyxel.rndi(0, 1)]                               # random direction
            chosen.dy = -1
            
            # trajectory
            u,v = chosen.x, chosen.y
            a,b= self.playerx, self.playery

            chosen.trajectory =  []
            
            dx=(a-u) # 敵と自機の間隔を10分割したデルタを考える そしてキャラクターのサイズよりデルタは大きくする
            dy=(b-v)
            dist=(dx**2+dy**2)**.5

            dx=dx/dist*16 # unit vector x16
            dy=dy/dist*16 # unit vector x16

            #if a<u:dx*=-1 # direction should be opposite

            __x=u
            while 1:
                
                # linear
                __y=(b-v)/(a-u)*(__x-u)+v
                
                mx=(a+u)/2
                my=(b+v)/2

                #__y=1*(__x-u)*(__x-a)*(__x-mx)+(b-v)/(a-u)*(__x-u)+v  # if __x==u, __y=v , if __x==a, __y==b , if __x==mx, __y= my

                chosen.trajectory.append([__x,__y])
                if __x<0 or APP_WIDTH<__x or __y<0 or APP_HEIGHT<__y:break
                __x+=dx

        [enemy.update(self.x,self.y)for row in self.list for enemy in row]

        # player update
        player_dx,player_dy= playercontrol()

        self.playerx = min(APP_WIDTH -CHAR_SIZE,max(0, self.playerx+player_dx))# clamping
        self.playery = min(APP_HEIGHT-CHAR_SIZE,max(0, self.playery+player_dy)) # extended y move , and clamping
    
    def draw(self):
        [enemy.draw()for row in self.list for enemy in row]
        
        # (debug) middle point to draw 
        for row in self.list:
            for enemy in row:
                if enemy.is_flying and not enemy.is_return:
                    mx=(enemy.x+self.playerx)/2
                    my=(enemy.y+self.playery)/2
                    pyxel.circ(mx,my,3,6) 

        # player position
        pyxel.circ(self.playerx,self.playery,4,7)
        pyxel.text(self.playerx,self.playery + 16, f'{int(self.playerx)},{int(self.playery)}', 7)

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
        pyxel.circ(self.x, self.y,4,6)

        # debug display
        if self.is_flying: 
            pyxel.text(self.x, self.y + 16, f'{int(self.x)},{int(self.y)}', 7)
            for p1, p2 in zip(self.trajectory, self.trajectory[1:]):
                pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)
                pyxel.circ(p1[0], p1[1], 2,7)

class App:
    def __init__(self):
        pyxel.init(APP_WIDTH, APP_HEIGHT, title="Kanixian MOD", fps=120)
        self.squad = Squad()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.squad.update()
                
    def draw(self):
        pyxel.cls(0)
        self.squad.draw()
                
App()