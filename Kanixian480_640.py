import pyxel , math

debugdisp=0

APP_WIDTH = 480
APP_HEIGHT = 640
CHAR_SIZE=16 

class Star:
    def __init__(self):
        self.x = pyxel.rndi(0,APP_WIDTH )
        self.y = pyxel.rndi(0,APP_HEIGHT)
        self.color = pyxel.rndi(5,7)
        self.speed =  self.color/4 -1

    def update(self):
        self.y += self.speed* ( App.stage_number+1)* 0.2 # scroll
        self.y %= APP_HEIGHT

    def draw(self):
        if pyxel.rndi(1,self.color-2) <3 :#blinking. showing at 33%
            pyxel.pset(self.x,self.y,self.color)

class Message:# hit score on screen 
    def __init__(self,x,y,message) -> None:
        self.x, self.y = x, y
        self.cnt = 30 # timer 
        self.mes = message
    def update(self):
        self.y -= 0.2 # position move
        self.cnt -= 1 # timer decrement
    def draw(self):
        pyxel.text(self.x,self.y,self.mes,7)

class Squad:
    def __init__(self):
        self.x, self.y = CHAR_SIZE*6, CHAR_SIZE*4
        self.dx = 0.2
        self.dy = 0
        self.list = [[],[],[],[]] # enemy arrays

    def update(self):
        self.x += self.dx # horizontal group move

        theta= pyxel.frame_count/180*math.pi
        #print(theta)
        self.y += math.sin(theta) * 0.25 # *CHAR_SIZE
        if not (CHAR_SIZE <= self.x <= CHAR_SIZE*9): self.dx *= -1 # reverse direction

        ### 移動開始させるかどうかの判定
        attack_interval=max(1,60-App.stage_number*4)# dynamic interval dependent on stage number

        if pyxel.frame_count % attack_interval == 0:
            print(f'debug teki_flyable:{App.flyable_enemy_count} @ {pyxel.frame_count}')

            if App.flyable_enemy_count:
                App.flyable_enemy_count -= 1
                enemy_alive=[enemy for row in enemy_group.list for enemy in row]
                chosen=enemy_alive[pyxel.rndi(0,len(enemy_alive)-1)] # choose at random
                chosen.is_flying = True
                chosen.dx= (-1,1)[pyxel.rndi(0,1)]
                chosen.fly()
                
        ### list中の敵が弾に当たったかの判定と削除
        for row in reversed(range(len(enemy_group.list))):
            for teki in self.list[row]:
                for bullet in App.bullet_list:
                    if bullet.check_hit(teki.x,teki.y):
                        App.flyable_enemy_count+=teki.is_flying                                     # another enemy can fly 
                        ds =teki.is_flying and (30,150)[row==0]or 10                                # set delta of score
                        App.score += ds                                                             # increase score
                        App.message_list.append(Message(teki.x+4+2*(ds==150),teki.y+6,f"{ds}"))     # add score text
                        self.list[row].remove(teki)                                                 # remove enemy
                        App.bullet_list.remove(bullet)                                              # remove bullet
                        pyxel.play(1,1)                                                             # play sound effect


enemy_group = Squad() 

class Teki:
    def __init__(self,rx,ry,num): # rx,ry: relative position in group, num: row id from top
        self.rposx = rx
        self.rposy = ry
        self.num = min(3,num)
        self.cnt = pyxel.rndi(0,60) # used for animation pattern randomness
        self.is_flying = False # flying
        self.is_return = False
        self.x = enemy_group.x + self.rposx # final position to draw
        self.y = enemy_group.y + self.rposy
        self.dx=0
        self.dy=0
        self.trajectory = []

    def move(self,tx,ty):
        vx=tx-self.x
        vy=ty-self.y
        dist = (vx*vx + vy*vy)**.5
        self.dx = vx / dist * 2
        self.dy = vy / dist * 2
        self.x += self.dx
        self.y += self.dy

        return abs(vx)<1 and abs(vy)<1

    def update(self):
        self.cnt += 1

        # returning, flying or moving as the group member
        if self.is_return: 
            # enemy is out of screen, returning to the target position aka default position
            tx=enemy_group.x + self.rposx
            ty=enemy_group.y + self.rposy
            if self.move(tx,ty): # if arrived the destination
                self.is_flying = False # otherwise, enemy starts to fly again
                self.is_return = False

        elif self.is_flying:
            # enemy is not in squad any more, flying along its trajectory
            tx,ty = self.trajectory[0]# target position
            if self.move(tx,ty): # if arrived the destination, next target
                self.trajectory.pop(0)

            if 100 - App.stage_number < self.y < 104 + App.stage_number: # enemy bullet shoot range : extend it by stage number
                App.tekibullets.append(TekiBullet(self.x-16+pyxel.rndi(0,16) , self.y+16 , (self.dx * pyxel.rndf(1,2))/4))

            if APP_HEIGHT + 32 < self.y : # out of screen, so teleport it to the top of the screen
                self.is_return = True
                self.y = -CHAR_SIZE*2
                self.x = APP_WIDTH / 2
                App.flyable_enemy_count += 1
            
        else:
            # default behavior : enemy moves as the group
            self.x = enemy_group.x + self.rposx
            self.y = enemy_group.y + self.rposy

    def draw(self):
        # pyxel.blt(x,y,atlas_image,u,v,w,h, mask_color) 
        u=self.is_flying and 2+(0<self.dx) or (self.cnt//30)%2  # animation pattern 
        v=self.num+3 # enemy color by row id
        pyxel.blt(self.x,self.y,0, u*16 ,v*16 ,16,16,0)

        if debugdisp and self.is_flying:
            pyxel.text(self.x,self.y+16,f'{int(self.x)},{int(self.y)}',7)
            for p1,p2 in zip(self.trajectory,self.trajectory[1:]):
                pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)

    def fly(self): # shared logic
        self.is_flying = True
        px=self.x+myship.x
        py=self.y+myship.y
        self.trajectory = [[self.x+32*self.dx,self.y-32],[self.x+64*self.dx,self.y+10],[self.x-16+16*self.dx,self.y+20]]
        self.trajectory +=[[px/4,py/4], [px/3,py/3], [px/2,py/2],  [px/3*2,py/3*2],[px/4*3,py/4*3],[myship.x,myship.y],[px/2*3,py/2*3],[self.x, APP_HEIGHT+64]] # last pos should be out of screen
        self.dy = -1

    def check_hit(self,shipx,shipy) :
        return abs(shipx - self.x) < 12 and abs(shipy - self.y) < 12


class BulletBase:
    def __init__(self, x, y, dx=0, dy=0, w=2, h=4, c=10) -> None:
        self.x,self.y  = x, y
        self.dx , self.dy = dx, dy
        self.whc =(w,h,c) # width , height, color
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        pyxel.rect(self.x, self.y, *self.whc)

class Bullet(BulletBase):  # my bullet
    def __init__(self, x, y) -> None:
        super().__init__(x, y, dy=-3, h=4, c=10)
        
    def check_hit(self, tekix, tekiy):
        return self.x - CHAR_SIZE < tekix < self.x and self.y - CHAR_SIZE < tekiy < self.y

class TekiBullet(BulletBase):
    def __init__(self, x, y, dx) -> None:
        super().__init__(x, y, dx=dx, dy=1, h=8, c=7)
    
    def check_hit(self, shipx, shipy):
        return self.x - CHAR_SIZE + 2 < shipx < self.x - 2 and self.y - CHAR_SIZE + 2 < shipy < self.y - 2


class Myship:
    def __init__(self) -> None:
        self.x = (APP_WIDTH-CHAR_SIZE)/2 # center 
        self.y = APP_HEIGHT - CHAR_SIZE*4
        self.img=4 # default image to display

    def update(self): ### user input to move myship
        move_R=pyxel.btn(pyxel.KEY_RIGHT)   or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        move_L=pyxel.btn(pyxel.KEY_LEFT)    or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        move_D=pyxel.btn(pyxel.KEY_DOWN)    or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
        move_U=pyxel.btn(pyxel.KEY_UP)      or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)

        dx=move_R or -move_L # 1 or -1 or 0
        dy=move_D or -move_U # 1 or -1 or 0
        self.img=move_R*2 or move_L*3 or 4 # 2 or 3 or 4

        self.x = min(APP_WIDTH -CHAR_SIZE,max(0, self.x+dx))# clamping
        self.y = min(APP_HEIGHT-CHAR_SIZE,max(0, self.y+dy)) # extended y move , and clamping

    def draw(self):
        pyxel.blt(self.x,self.y,0,self.img*CHAR_SIZE,CHAR_SIZE,CHAR_SIZE,24,0) # change image dependent on its direction

myship = Myship()


class App:
    # moved global variable here by using App.variablename 
    score = 0
    flyable_enemy_count=0
    stage_number=0 
    message_list = []# moved the variable here instead of global variable
    bullet_list = []
    tekibullets = []
    
    def __init__(self):
        pyxel.init(APP_WIDTH,APP_HEIGHT,title="Kanixian MOD",fps=120,display_scale=1) 
        pyxel.load("kani.pyxres")
        try:
            with open("hiscore.txt","r") as f:self.hiscore = int(f.readline())
        except:
            self.hiscore=0

        self.stars=[Star()for i in range(60)]#background stars
        self.init_game()
        pyxel.run(self.update,self.draw)

    def init_game(self):
        App.stage_number=0

        if App.score > self.hiscore:
            self.hiscore = App.score
            with open("hiscore.txt","w") as f:f.write(f'{self.hiscore}')
        self.is_gaming = False

        myship.__init__() # need this with vertical freedom, otherwise instant gameover 

    def init_stage(self):
        App.bullet_list = []# need to empty otherwise, instant death could happen
        App.tekibullets = []# need to empty otherwise, instant death could happen
        App.stage_number += 1
        App.flyable_enemy_count = App.stage_number + 1 # simultaneous fly increases
        self.counter = 0
        MAX_COL_NUM=16*2
        enemy_group.list = [[Teki(x*10,i*20,i)for x in R] for i, R in enumerate( [(4+3*2,10+5*2),range(2,MAX_COL_NUM-2,2)]+[range(0,MAX_COL_NUM,2)]*5 )]

    def update(self):
        for star in self.stars:
            star.update()

        ### ゲーム開始の判定
        if self.is_gaming == False:
            if (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)):
                score = 0
                self.init_stage()
                self.is_gaming = True
            return
        
        ### ステージクリアの判定
        if sum(map(len,enemy_group.list))==0:
            self.init_stage()
            return
            
        ### ゲームオーバーの判定  enemy or enemy bullet hit the player
        obstacles=App.tekibullets+sum(enemy_group.list,[])
        for obs in obstacles:
            if obs.check_hit(myship.x,myship.y):
                pyxel.play(2,2)
                self.init_game()
                return

        ### ステージ開始からの経過フレーム数の更新
        self.counter += 1

        ### 弾発射の判定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            App.bullet_list.append(Bullet(myship.x + 7,myship.y))
            pyxel.play(0,0)

        ### 弾の生存確認
        [App.bullet_list.remove(bullet)for bullet in App.bullet_list if bullet.y < -10]
        [App.tekibullets.remove(bullet) for bullet in App.tekibullets if bullet.y > APP_HEIGHT + 10]

        [App.message_list.remove(mes)for mes in App.message_list if mes.cnt < 0]    # メッセージの生存確認
        myship.update()                                                     # 自機の更新 # position by direction
        [bullet.update() for bullet in App.bullet_list+App.tekibullets]             # 弾の更新
        enemy_group.update()                                                # 分隊の更新
        [teki.update() for tekis in enemy_group.list for teki in tekis]     # 敵の更新
        [mes.update() for mes in App.message_list]                              # メッセージの更新            

    def draw(self):
        pyxel.cls(0)

        # background
        [star.draw() for star in self.stars]

        # core contents
        if self.is_gaming:            
            [teki.draw() for tekis in enemy_group.list for teki in tekis]   # 敵の描画
            [bullet.draw() for bullet in App.bullet_list+App.tekibullets]           # 弾の描画
            myship.draw()                                                   # 自機の描画
            [mes.draw() for mes in App.message_list]                            # メッセージの描画
            pyxel.text( APP_WIDTH//8*7,10,   f"{App.score}" ,7)                 # score info
            pyxel.text(10,10,f"STAGE : {App.stage_number}",7)                   # stage info
        else:
            pyxel.blt(APP_WIDTH//4,APP_HEIGHT//2-50,2,0,32,256,48,0)                                   # title image
            pyxel.text(82+APP_WIDTH//4,APP_HEIGHT//2+50,"Push BUTTON to Start",pyxel.frame_count%30)    # push to start message
            pyxel.text(APP_WIDTH//2+180,APP_HEIGHT-50,"MOD 0.1",7)                                      # version info

        # UI 
        pyxel.text( (APP_WIDTH)//5*2,10,    f"HI-SCORE : {self.hiscore}",7) # hi-score to display

        # debug info
        if debugdisp:
            pyxel.text( 16,APP_HEIGHT-16,   f"self.is_gaming:{self.is_gaming}" ,7) # score info
App()