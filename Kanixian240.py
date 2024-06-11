import pyxel

APP_WIDTH = APP_HEIGHT = 240

star_list = []
message_list = []
score = 0

debugdisp=True

class Message():# hit score on screen 
    def __init__(self,x,y,message) -> None:
        self.x = x
        self.y = y
        self.cnt = 30 # timer 
        self.mes = message
    def update(self):
        self.cnt -= 1 # timer decrement
        self.y -= 0.2 # position move
    def draw(self):
        pyxel.text(self.x,self.y,self.mes,7)

class Squad():   # 分隊
    def __init__(self,x=12,y=16) -> None:
        self.start_x = x  # 分隊全体の左上の座標
        self.x = x
        self.y = y
        self.dx = 0.2
        self.list = [[],[],[],[]]
        self.counter = 1
        self.interval = 60 # attach interval

    def update(self):
        global teki_flyable,score,message_list
        self.counter += 1
        self.x += self.dx


        if self.x > self.start_x + 60:
            self.x = self.start_x + 60
            self.dx = -self.dx
        elif self.x < self.start_x:
            self.x = self.start_x
            self.dx = -self.dx

        ### 移動開始させるかどうかの判定
        if self.counter % self.interval == 0:

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
                for bullet in bullets:
                    if bullet.check_hit(teki.x,teki.y):

                        if teki.is_flying:
                            teki_flyable += 1
                            ds=y and 30 or 150   

                        else:ds=10
                        score += ds
                        message_list.append(Message(teki.x+4+2*(ds==150),teki.y+6,f"{ds}"))
                        self.list[y].remove(teki)
                        bullets.remove(bullet)
                        pyxel.play(1,1)

squad_inst = Squad() 

class Teki():
    def __init__(self,rx,ry,num) -> None:
        self.rposx = rx # it seems rx means relative position x before squad move 
        self.rposy = ry
        self.cnt = pyxel.rndi(0,100)
        self.num = num
        self.is_flying = False # flying
        self.is_return = False
        self.x = squad_inst.x + self.rposx # final position to draw
        self.y = squad_inst.y + self.rposy
        self.dest_list = []

    def update(self):
        global teki_flyable
        self.cnt += 1

        if self.is_return:
            print('self.is_return...')
            self.x = (self.x + squad_inst.x + self.rposx) / 2
            self.y = (self.y + squad_inst.y + self.rposy) / 2
            if round(self.x) == round(squad_inst.x + self.rposx) and round(self.y) == round(squad_inst.y + self.rposy):
                self.is_flying = False
                self.is_return = False

        elif self.is_flying:

            self.x += self.dx
            self.y += self.dy

            dest = self.dest_list[0]

            rx = abs(self.x - dest[0]) 
            ry = abs(self.y - dest[1])
            
            if rx < 1 and ry < 1:
                self.dest_list.pop(0)
                if len(self.dest_list) == 0:
                    self.is_flying = False
                else:
                    dest = self.dest_list[0]
                    vec_dx = (dest[0] - self.x)
                    vec_dy = (dest[1] - self.y)
                    vec_len = (vec_dx * vec_dx + vec_dy * vec_dy)**.5
                    self.dx = (vec_dx / vec_len) * 2
                    self.dy = (vec_dy / vec_len) * 2
            if self.y > 100 and self.y < 104:
                tekibullets.append(TekiBullet(self.x-16+pyxel.rndi(0,16),self.y+16,(self.dx * pyxel.rndf(1,2))/4))
            if self.y > APP_HEIGHT + 32:
                self.y = -16
                self.is_return = True
                teki_flyable += 1
            
        else:
            #print('phase else...')
            self.x = squad_inst.x + self.rposx
            self.y = squad_inst.y + self.rposy

    def draw(self):
        # pyxel.blt(x,y,atlas_image,u,v,w,h, mask_color) 
        u=self.is_flying and 2+(0<self.dx) or (self.cnt//24)%2 
        v=self.num+3
        pyxel.blt(self.x,self.y,0, u*16 ,v*16 ,16,16,0)

        if debugdisp and self.is_flying:
            pyxel.text(self.x,self.y+16,f'{int(self.x)},{int(self.y)}',7)

    def start_core(self): # shared logic
        px=self.x+myship.x
        py=self.y+myship.y
        self.dest_list += [  [px/4,py/4], [px/3,py/3], [px/2,py/2],  [px/3*2,py/3*2],   [px/4*3,py/4*3],   [myship.x,myship.y],   [px/2*3,py/2*3],  [self.x,APP_HEIGHT+64]]
        self.dy = -1
        self.is_flying = True

    def start_right(self):# enemy move from rightside
        self.dest_list = [            [self.x+32,self.y-32],[self.x+64,self.y+10],[self.x,self.y+20]        ]
        self.start_core()
        self.dx =  1
    def start_left(self):# enemy move from leftside
        self.dest_list = [            [self.x-32,self.y-32],[self.x-64,self.y+10],[self.x-32,self.y+20]        ]
        self.start_core()
        self.dx = -1

    def check_hit(self,shipx,shipy) -> bool:
        return abs(shipx - self.x) < 12 and abs(shipy - self.y) < 12

class Star():
    def __init__(self):
        self.x = pyxel.rndi(0,APP_WIDTH )
        self.y = pyxel.rndi(0,APP_HEIGHT)
        self.color = pyxel.rndi(5,7)
        self.speed = -1 + pyxel.rndf(0.0,0.25)+ self.color/4

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
        self.dx = dx
    
    def update(self):
        self.x += self.dx
        self.y += 1
    
    def draw(self):
        pyxel.rect(self.x,self.y,2,8,7)

    def check_hit(self,shipx,shipy):
        return self.x-14 < shipx < self.x-3 and self.y-14 < shipy < self.y-2

class Myship():
    def __init__(self) -> None:
        self.x = (APP_WIDTH-16)/2 # center 
        self.y = APP_HEIGHT - 32
        self.dx=0
        self.dy=0
        self.dir = 4 # using for id to display image

    def update(self):
        
        ### 自機移動
        self.dx=0
        self.dy=0
        if pyxel.btn(pyxel.KEY_DOWN)    or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):  self.dy=1
        if pyxel.btn(pyxel.KEY_UP)      or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):    self.dy=-1

        if pyxel.btn(pyxel.KEY_RIGHT)   or  10000 <pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<36000      or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.dx=1
        if pyxel.btn(pyxel.KEY_LEFT)    or  -36000<pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)<-10000     or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):  self.dx=-1

        self.x = min(APP_WIDTH-16,max(0,self.x+self.dx))# clamping
        self.y = min(APP_HEIGHT-16,max(0, self.y+self.dy)) # extended y move , and clamping

        #dx,dy =([0,1],[0,-1],[1,0],[-1,0], [0,0])[self.dir] # made speed x1 
        if self.dx==1:self.dir=2
        if self.dx==-1:self.dir=3
        if self.dx==0:self.dir=4
        if debugdisp: print(self.dx, self.dy)

    def draw(self):

        pyxel.blt(self.x,self.y,0,self.dir*16,16,16,24,0) # change image dependent on its direction

myship = Myship()


class App():
    def __init__(self):
        pyxel.init(APP_WIDTH,APP_HEIGHT,title="Kanixian MOD",fps=60,display_scale=2) 
        pyxel.load("kani.pyxres")

        for i in range(50):       ### 背景として流れる★
            star_list.append(Star())
        try:
            with open("hiscore.txt","r") as f:
                self.hiscore = int(f.readline())
        except:
            self.hiscore=0
            with open("hiscore.txt","w") as f:
                f.write(str(self.hiscore))

        self.init_game()
        pyxel.run(self.update,self.draw)

    def init_game(self):
        if score > self.hiscore:
            self.hiscore = score
            with open("hiscore.txt","w") as f:
                f.write(str(self.hiscore))
        self.stage_number = 0
        self.is_gaming = False

    def init_stage(self):
        global teki_flyable,bullets,tekibullets,score
    
        bullets = []
        tekibullets = []
        self.stage_number += 1
        teki_flyable = self.stage_number + 1
        squad_inst.interval = 120 - self.stage_number*6 # interval changed dependent on stage_number
        self.counter = 0
        
        squad_inst.list = [
            [Teki(x*10,0,0) for x in (4,10)],
            [Teki(x*10,20,1) for x in range(2,14,2)],
            [Teki(x*10,40,2) for x in range(0,16,2)],
            [Teki(x*10,60,3) for x in range(0,16,2)],
        ]

    def update(self):
        global score

        ### ★の更新
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
        if sum(map(len,squad_inst.list))==0:
            self.init_stage()
            return
            
        ### ゲームオーバーの判定
        obstacles=tekibullets+sum(squad_inst.list,[])
        for obs in obstacles:
            if obs.check_hit(myship.x,myship.y):
                pyxel.play(2,2)
                self.init_game()
                return

        ### ステージ開始からの経過フレーム数の更新
        self.counter += 1

        ### 弾発射の判定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            bullets.append(Bullet(myship.x + 7,myship.y))
            pyxel.play(0,0)

        ### 弾の生存確認
        [bullets.remove(bullet)for bullet in bullets if bullet.y < -10]
        [tekibullets.remove(bullet) for bullet in tekibullets if bullet.y > APP_HEIGHT + 10]

        [message_list.remove(mes)for mes in message_list if mes.cnt < 0]    ### メッセージの生存確認
        myship.update()                                             ### 自機の更新 # position by direction
        [bullet.update() for bullet in bullets+tekibullets]         ### 弾の更新
        squad_inst.update()                                              ### 分隊の更新
        [teki.update() for tekis in squad_inst.list for teki in tekis]   ### 敵の更新
        [mes.update() for mes in message_list]                          ### メッセージの更新            

    def draw(self):
        pyxel.cls(0)

        # background
        [star.draw() for star in star_list]

        # core contents
        if self.is_gaming:            
            myship.draw()                                           ### 自機の描画
            [bullet.draw() for bullet in bullets+tekibullets]       ### 弾の描画
            [teki.draw() for tekis in squad_inst.list for teki in tekis] ### 敵の描画
            [mes.draw() for mes in message_list]                    ### メッセージの描画

            pyxel.text( APP_WIDTH//8*7,10,   f"{score}" ,7) # score info

            ### ステージ番号の描画
            pyxel.text(10,10,f"STAGE : {self.stage_number}",7)                             # `stage` info
            
        else:### ゲーム開始してないときの描画
            pyxel.text(82,150,"Push BUTTON to Start",pyxel.frame_count%16)  # push to start message
            pyxel.blt(-4,100,2,0,32,256,48,0)                               # title image
            pyxel.text(200,220,"MOD 0.1",7)                                 # version info

        # UI 
        pyxel.text( (APP_WIDTH)//5*2,10,    f"HI-SCORE : {self.hiscore}",7) # hi-score to display
App()