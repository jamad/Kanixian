import pyxel

debugdisp=0

APP_WIDTH = APP_HEIGHT = 240
CHAR_SIZE=16 

star_list = []
message_list = []
score = 0

stage_number=0 # used in App, Squad


class Message():# hit score on screen 
    def __init__(self,x,y,message) -> None:
        self.x, self.y = x, y
        self.cnt = 30 # timer 
        self.mes = message
    def update(self):
        self.y -= 0.2 # position move
        self.cnt -= 1 # timer decrement
    def draw(self):
        pyxel.text(self.x,self.y,self.mes,7)

class Squad():   # 分隊
    def __init__(self) -> None:
        self.x, self.y = 12, 16
        self.dx = 0.2
        self.list = [[],[],[],[]]# enemy arrays
        self.counter = 1
        #self.interval = 60 #  interval to attack

    def update(self):
        global teki_flyable,score,message_list, stage_number
        self.counter += 1

        self.x += self.dx # horizontal group move
        if 72 <self.x or self.x < 12: self.dx *= -1 # reverse direction

        ### 移動開始させるかどうかの判定

        attack_interval=max(1,60-stage_number*4)# dynamic interval dependent on stage number

        if self.counter % attack_interval == 0:
            print(f'debug teki_flyable:{teki_flyable} @ {self.counter}')
            if teki_flyable:
                while(row:=self.list[pyxel.rndi(0,3)])==[]:continue # select non empty row at random 
                col=pyxel.rndi(0,len(row)-1)# choose col at random
                row[col].is_flying == False

                # 50% randomness to fly from left or right
                if pyxel.rndi(0,1):row[col].start_left()
                else:row[col].start_right()

                teki_flyable -= 1

        ### list中の敵が弾に当たったかの判定と削除
        for y in reversed(range(4)):
            for teki in self.list[y]:
                for bullet in bullet_list:
                    if bullet.check_hit(teki.x,teki.y):

                        if teki.is_flying:
                            teki_flyable += 1
                            ds=y and 30 or 150   

                        else:ds=10
                        score += ds
                        message_list.append(Message(teki.x+4+2*(ds==150),teki.y+6,f"{ds}"))
                        self.list[y].remove(teki)
                        bullet_list.remove(bullet)
                        pyxel.play(1,1)

enemy_group = Squad() 

class Teki():
    def __init__(self,rx,ry,num): # rx,ry: relative position in group, num: row id from top
        self.rposx = rx
        self.rposy = ry
        self.num = num
        self.cnt = pyxel.rndi(0,60) # used for animation pattern randomness
        self.is_flying = False # flying
        self.is_return = False
        self.x = enemy_group.x + self.rposx # final position to draw
        self.y = enemy_group.y + self.rposy
        self.trajectory = []

    def update(self):
        global teki_flyable
        self.cnt += 1

        # returning, flying or moving as the group member
        if self.is_return: 
            # enemy is out of screen, returning to the default position
            
            self.x = (self.x + enemy_group.x + self.rposx) / 2
            self.y = (self.y + enemy_group.y + self.rposy) / 2

            if round(self.x) == round(enemy_group.x + self.rposx) and round(self.y) == round(enemy_group.y + self.rposy):
                self.is_flying = False
                self.is_return = False

        elif self.is_flying:
            # enemy is not in squad any more, flying along its trajectory

            self.x += self.dx
            self.y += self.dy

            tx,ty = self.trajectory[0]# target position

            rx = abs(self.x - tx) 
            ry = abs(self.y - ty)
            
            if rx < 1 and ry < 1: # if arrived the destination
                self.trajectory.pop(0)

            if len(self.trajectory) == 0:
                self.is_flying = False
            else:
                dest = self.trajectory[0] # next destination

                vec_dx = (dest[0] - self.x)
                vec_dy = (dest[1] - self.y)
                dist = (vec_dx * vec_dx + vec_dy * vec_dy)**.5
                self.dx = vec_dx / dist * 2
                self.dy = vec_dy / dist * 2

            if 100 < self.y < 104: # shooting the bullet
                tekibullets.append(TekiBullet(self.x-16+pyxel.rndi(0,16) , self.y+16 , (self.dx * pyxel.rndf(1,2))/4))

            if self.y > APP_HEIGHT + 32:
                self.y = -16
                self.is_return = True
                teki_flyable += 1
            
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
            for p1,p2 in zip(self.trajectory,self.trajectory[1:]):pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)

    def start_core(self): # shared logic
        self.is_flying = True
        px=self.x+myship.x
        py=self.y+myship.y
        self.trajectory += [  [px/4,py/4], [px/3,py/3], [px/2,py/2],  [px/3*2,py/3*2],[px/4*3,py/4*3],[myship.x,myship.y],[px/2*3,py/2*3],[self.x, APP_HEIGHT+64]] # last pos should be out of screen
        self.dy = -1

    def start_right(self):# enemy move from rightside
        self.trajectory = [            [self.x+32,self.y-32],[self.x+64,self.y+10],[self.x,self.y+20]        ]
        self.start_core()
        self.dx = 1

    def start_left(self):# enemy move from leftside
        self.trajectory = [            [self.x-32,self.y-32],[self.x-64,self.y+10],[self.x-32,self.y+20]        ]
        self.start_core()
        self.dx = -1

    def check_hit(self,shipx,shipy) -> bool:
        return abs(shipx - self.x) < 12 and abs(shipy - self.y) < 12

class Star():
    def __init__(self):
        self.x = pyxel.rndi(0,APP_WIDTH )
        self.y = pyxel.rndi(0,APP_HEIGHT)
        self.color = pyxel.rndi(5,7)
        self.speed =  self.color/4 -1

    def update(self):
        self.y += self.speed # scroll

    def draw(self):
        if pyxel.rndi(1,3) <2 :#blinking. showing at 33%
            pyxel.pset(self.x,self.y,self.color)

class Bullet():# my bullet
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def update(self):
        self.y -= 3 # changed from 4 to 3

    def draw(self):
        pyxel.rect(self.x,self.y,2,4,10)
        
    def check_hit(self,tekix,tekiy):
        return self.x-16 < tekix < self.x and self.y-16 < tekiy < self.y

class TekiBullet():
    def __init__(self,x,y,dx) -> None:
        self.x = x
        self.y = y
        self.dx = dx # horizontal velocity
    
    def update(self):
        self.x += self.dx
        self.y += 1
    
    def draw(self):
        pyxel.rect(self.x,self.y,2,8,7)

    def check_hit(self,shipx,shipy):
        return self.x-14 < shipx < self.x-2 and self.y-14 < shipy < self.y-2

class Myship():
    def __init__(self) -> None:
        self.x = (APP_WIDTH-16)/2 # center 
        self.y = APP_HEIGHT - 32
        self.img=4 # used for image to display

    def update(self): ### 自機移動
        dx,dy,self.img=0,0,4

        # user input for myship to move
        if pyxel.btn(pyxel.KEY_RIGHT)   or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): dx=1;   self.img=2
        if pyxel.btn(pyxel.KEY_LEFT)    or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):  dx=-1;  self.img=3
        if pyxel.btn(pyxel.KEY_DOWN)    or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):  dy=1
        if pyxel.btn(pyxel.KEY_UP)      or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):    dy=-1

        self.x = min(APP_WIDTH-16,max(0,self.x+dx))# clamping
        self.y = min(APP_HEIGHT-16,max(0, self.y+dy)) # extended y move , and clamping

    def draw(self):
        pyxel.blt(self.x,self.y,0,self.img*16,16,16,24,0) # change image dependent on its direction

myship = Myship()


class App():
    def __init__(self):
        pyxel.init(APP_WIDTH,APP_HEIGHT,title="Kanixian MOD",fps=60,display_scale=2) 
        pyxel.load("kani.pyxres")
        try:
            with open("hiscore.txt","r") as f:self.hiscore = int(f.readline())
        except:
            self.hiscore=0
            with open("hiscore.txt","w") as f:f.write(f'{self.hiscore}')

        for i in range(50):star_list.append(Star())### 背景として流れる★
        self.init_game()
        pyxel.run(self.update,self.draw)

    def init_game(self):
        global stage_number
        stage_number=0

        if score > self.hiscore:
            self.hiscore = score
            with open("hiscore.txt","w") as f:
                f.write(str(self.hiscore))
        self.is_gaming = False

        myship.__init__() # need this with vertical freedom, otherwise instant gameover 

    def init_stage(self):
        global teki_flyable,bullet_list,tekibullets,score,stage_number
        
        bullet_list = []# need to empty otherwise, instant death could happen
        tekibullets = []# need to empty otherwise, instant death could happen
    
        stage_number += 1
        teki_flyable = stage_number + 1
        self.counter = 0
        enemy_group.list = [[Teki(x*10,i*20,i) for x in R] for i, R in enumerate( ((4,10),range(2,14,2),range(0,16,2), range(0,16,2) ))]

    def update(self):
        global score

        for star in star_list:
            star.update()
            if star.y > APP_HEIGHT:
                star_list.remove(star)
                star_list.append(Star())

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
            
        ### ゲームオーバーの判定
        obstacles=tekibullets+sum(enemy_group.list,[])
        for obs in obstacles:
            if obs.check_hit(myship.x,myship.y):
                pyxel.play(2,2)
                self.init_game()
                return

        ### ステージ開始からの経過フレーム数の更新
        self.counter += 1

        ### 弾発射の判定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            bullet_list.append(Bullet(myship.x + 7,myship.y))
            pyxel.play(0,0)

        ### 弾の生存確認
        [bullet_list.remove(bullet)for bullet in bullet_list if bullet.y < -10]
        [tekibullets.remove(bullet) for bullet in tekibullets if bullet.y > APP_HEIGHT + 10]

        [message_list.remove(mes)for mes in message_list if mes.cnt < 0]    ### メッセージの生存確認
        myship.update()                                             ### 自機の更新 # position by direction
        [bullet.update() for bullet in bullet_list+tekibullets]         ### 弾の更新
        enemy_group.update()                                              ### 分隊の更新
        [teki.update() for tekis in enemy_group.list for teki in tekis]   ### 敵の更新
        [mes.update() for mes in message_list]                          ### メッセージの更新            

    def draw(self):
        global stage_number

        pyxel.cls(0)

        # background
        [star.draw() for star in star_list]

        # core contents
        if self.is_gaming:            
            myship.draw()                                           ### 自機の描画
            [bullet.draw() for bullet in bullet_list+tekibullets]       ### 弾の描画
            [teki.draw() for tekis in enemy_group.list for teki in tekis] ### 敵の描画
            [mes.draw() for mes in message_list]                    ### メッセージの描画

            pyxel.text( APP_WIDTH//8*7,10,   f"{score}" ,7) # score info

            ### ステージ番号の描画
            pyxel.text(10,10,f"STAGE : {stage_number}",7)                             # `stage` info
            
        else:### ゲーム開始してないときの描画
            pyxel.text(82,150,"Push BUTTON to Start",pyxel.frame_count%16)  # push to start message
            pyxel.blt(-4,100,2,0,32,256,48,0)                               # title image
            pyxel.text(200,220,"MOD 0.1",7)                                 # version info

        # UI 
        pyxel.text( (APP_WIDTH)//5*2,10,    f"HI-SCORE : {self.hiscore}",7) # hi-score to display

        # debug info
        if debugdisp:
            pyxel.text( 16,APP_HEIGHT-16,   f"self.is_gaming:{self.is_gaming}" ,7) # score info
App()