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

        self.bezier_points=[]

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
            p0x,p0y = chosen.x, chosen.y
            p3x,p3y = self.playerx, self.playery
            
            # middle point
            mx=(p0x+p3x)/2
            my=(p0y+p3y)/2

            vector0_m=(mx-p0x, my-p0y)
            vector3_m=(mx-p3x, my-p3y)

            theta1=math.pi/2 # 45degree
            theta2=theta1/4  # 45degree

            p1x = p0x + vector0_m[0]*math.cos(theta1) - vector0_m[1]*math.sin(theta1)  # rotate vector0_m theta around p0 aka enemy
            p1y = p0y + vector0_m[0]*math.sin(theta1) + vector0_m[1]*math.cos(theta1)  # rotate vector0_m theta around p0 aka enemy

            p2x = p3x + vector3_m[0]*math.cos(theta2) - vector3_m[1]*math.sin(theta2)  # rotate vector0_m theta around p0 aka player
            p2y = p3y + vector3_m[0]*math.sin(theta2) + vector3_m[1]*math.cos(theta2)  # rotate vector0_m theta around p0 aka player

            chosen.trajectory =  []
            
            # 敵と自機の間隔を分割したデルタを考える 
            #dist=(dx**2+dy**2)**.5
            #dx=dx/dist*16 # unit vector x16
            #dy=dy/dist*16 # unit vector x16

            self.bezier_points=[(p0x,p0y),(p1x,p1y),(p2x,p2y),(p3x,p3y)]


            for T in range(32): # divided by 16 but twice to have the range out of 0<=t<=1 aka t<=2
                t=T/16
                u=1-t

                # bezier
                # n=3  p0,p1,p2,p3
                # B(t,i,n)= n!/((n-i)!*i!)  * t**i *(1-t)**(n-i)  #### 0<=t<=1
                # B(t,i,3)=3!/((3-i)!*i!) * t**i *(1-t)**(3-i)
                # Q(t)=[ p[i]*B(t,i,3)  for i in range(4)]  # i=0,1,2,3
                # Q(t)=sum ( [ p[i]*3!/((3-i)!*i!) *t**i * (1-t)**(3-i)  for i in range(4)]  )
                # Q(t): x =  p[0].x*(1-t)**3  +  p[1].x*3* t * (1-t)**2 + p[2].x*3* t**2 * (1-t)  +  p[3].x *t**3
                # Q(t): y =  p[0].y*(1-t)**3  +  p[1].y*3* t * (1-t)**2 + p[2].y*3* t**2 * (1-t)  +  p[3].y *t**3  

                __x =  p0x*u**3  +  p1x*3*t*u**2 + p2x*3*t**2*u  +  p3x*t**3
                __y =  p0y*u**3  +  p1y*3*t*u**2 + p2y*3*t**2*u  +  p3y*t**3  
                chosen.trajectory.append([__x,__y])

            chosen.trajectory.reverse()


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
                for x,y in self.bezier_points:
                    pyxel.circ(x,y,8,6) 

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