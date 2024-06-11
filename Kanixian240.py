import pyxel
import math

APP_WIDTH = APP_HEIGHT = 240
KEY = [pyxel.KEY_DOWN, pyxel.KEY_UP, pyxel.KEY_RIGHT, pyxel.KEY_LEFT]
D =   [[0,1],[0,-1],[1,0],[-1,0], [0,0]]
GPAD = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,        pyxel.GAMEPAD1_BUTTON_DPAD_UP,        pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT]
LAXIS = [pyxel.GAMEPAD1_AXIS_LEFTY,pyxel.GAMEPAD1_AXIS_LEFTY,         pyxel.GAMEPAD1_AXIS_LEFTX,pyxel.GAMEPAD1_AXIS_LEFTX]
LAXIS_RANGE = [[10000,36000],[-36000,-10000],[10000,36000],[-36000,-10000]]

stars = []
bullets = []
tekibullets = []
messages = []
score = 0

teki_movable = 0

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
    def __init__(self,x,y) -> None:
        self.start_x = x  # 分隊全体の左上の座標
        self.x = x
        self.y = y
        self.dx = 0.2
        self.list = [[],[],[],[]]
        self.counter = 1
        self.interval = 60
    def update(self):
        global teki_movable,score,messages
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
            if teki_movable > 0:
                gyou = self.list[pyxel.rndi(0,3)]
                while len(gyou) == 0:
                    gyou = self.list[pyxel.rndi(0,3)]
                if pyxel.rndi(0,1) == 0:
                    if gyou[0].is_move == False:
                        gyou[0].start_left()
                        teki_movable -= 1
                else:
                    if gyou[-1].is_move == False:
                        gyou[-1].start_right()
                        teki_movable -= 1

        ### list中の敵が弾に当たったかの判定と削除
        for y in reversed(range(4)):
            for teki in self.list[y]:
                for bullet in bullets:
                    if bullet.check_hit(teki.x,teki.y):
                        if teki.is_move:
                            teki_movable += 1
                            if y == 0:
                                score += 150
                                messages.append(Message(teki.x+6,teki.y+6,"150"))
                            else:
                                score += 30
                                messages.append(Message(teki.x+4,teki.y+6,"30"))
                        else:
                            messages.append(Message(teki.x+4,teki.y+6,"10"))
                            score += 10
                        self.list[y].remove(teki)
                        bullets.remove(bullet)
                        pyxel.play(1,1)

squad = Squad(12,16) 

class Teki():
    def __init__(self,rx,ry,num) -> None:
        self.rx = rx
        self.ry = ry
        self.cnt = pyxel.rndi(0,100)
        self.num = num
        self.is_move = False
        self.is_return = False
        self.x = squad.x + self.rx
        self.y = squad.y + self.ry
        self.dest_list = []

    def update(self):
        global teki_movable
        self.cnt += 1
        if self.is_return:
            self.x = (self.x + squad.x + self.rx) / 2
            self.y = (self.y + squad.y + self.ry) / 2
            if round(self.x) == round(squad.x + self.rx) and round(self.y) == round(squad.y + self.ry):
                self.is_move = False
                self.is_return = False
        elif self.is_move:
            self.x += self.dx
            self.y += self.dy
            dest = self.dest_list[0]
            rx = abs(self.x - dest[0])
            ry = abs(self.y - dest[1])
            if rx < 1 and ry < 1:
                self.dest_list.pop(0)
                if len(self.dest_list) == 0:
                    self.is_move = False
                else:
                    dest = self.dest_list[0]
                    vec_dx = (dest[0] - self.x)
                    vec_dy = (dest[1] - self.y)
                    vec_len = math.sqrt(vec_dx * vec_dx + vec_dy * vec_dy)
                    self.dx = (vec_dx / vec_len) * 2
                    self.dy = (vec_dy / vec_len) * 2
            if self.y > 100 and self.y < 104:
                tekibullets.append(TekiBullet(self.x-16+pyxel.rndi(0,16),self.y+16,(self.dx * pyxel.rndf(1,2))/4))
            if self.y > APP_HEIGHT + 32:
                self.y = -16
                self.is_return = True
                teki_movable += 1
            
        else:
            self.x = squad.x + self.rx
            self.y = squad.y + self.ry

    def draw(self):
        if self.is_move:
            if self.dx > 0:
                pyxel.blt(self.x,self.y,0,48,48+self.num*16,16,16,0)
            else:
                pyxel.blt(self.x,self.y,0,32,48+self.num*16,16,16,0)
        else:
            pyxel.blt(self.x,self.y,0,(self.cnt//24)%2*16,48+self.num*16,16,16,0)

    def start_right(self):
        self.dest_list = [
            [self.x+32,self.y-32],[self.x+64,self.y+10],
            [self.x,self.y+20],
            [(self.x+myship.x)/4,(self.y+myship.y)/4],
            [(self.x+myship.x)/3,(self.y+myship.y)/3],
            [(self.x+myship.x)/2,(self.y+myship.y)/2],
            [(self.x+myship.x)/3*2,(self.y+myship.y)/3*2],
            [(self.x+myship.x)/4*3,(self.y+myship.y)/4*3],
            [myship.x,myship.y],
            [(self.x+myship.x)/2*3,(self.y+myship.y)/2*3],
            [self.x,APP_HEIGHT+64]
        ]
        self.dx =  1
        self.dy = -1
        self.is_move = True
    def start_left(self):
        self.dest_list = [
            [self.x-32,self.y-32],[self.x-64,self.y+10],
            [self.x-32,self.y+20],
            [(self.x+myship.x)/4,(self.y+myship.y)/4],
            [(self.x+myship.x)/3,(self.y+myship.y)/3],
            [(self.x+myship.x)/2,(self.y+myship.y)/2],
            [(self.x+myship.x)/3*2,(self.y+myship.y)/3*2],
            [(self.x+myship.x)/4*3,(self.y+myship.y)/4*3],
            [myship.x,myship.y],
            [(self.x+myship.x)/2*3,(self.y+myship.y)/2*3],
            [self.x,APP_HEIGHT+64]
        ]
        self.dx = -1
        self.dy = -1
        self.is_move = True
    def check_hit(self,shipx,shipy) -> bool:
        if abs(shipx - self.x) < 12 and abs(shipy - self.y) < 12:
            return True
        return False

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

class Bullet():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def update(self):
        self.y -= 4

    def draw(self):
        pyxel.rect(self.x,self.y,2,4,10)
        
    def check_hit(self,tekix,tekiy):
        return self.x-14 < tekix < self.x-1 and self.y-16 < tekiy < self.y

class TekiBullet():
    def __init__(self,x,y,dx) -> None:
        self.x = x
        self.y = y
        self.dx = dx
    
    def update(self):
        self.y += 1
        self.x += self.dx
    
    def draw(self):
        pyxel.rect(self.x,self.y,2,8,7)

    def check_hit(self,shipx,shipy):
        return self.x-14 < shipx < self.x-3 and self.y-14 < shipy < self.y-2

class Myship():
    def __init__(self) -> None:
        self.x = APP_WIDTH / 2 - 8
        self.y = APP_HEIGHT - 32
        self.dir = 4 #移動無し
    def update(self):
        self.x += D[self.dir][0] * 2
        if self.x < 0:
            self.x = 0
        elif self.x > 223:
            self.x = 223
    def draw(self):
        pyxel.blt(self.x,self.y,0,self.dir*16,16,16,24,0)

myship = Myship()


class App():
    def __init__(self):
        pyxel.init(APP_WIDTH,APP_HEIGHT,title="Kanixian MOD",fps=60,display_scale=1) 
        pyxel.load("kani.pyxres")

        for i in range(50):       ### 背景として流れる★
            stars.append(Star())
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
        global teki_movable,bullets,tekibullets,score
        bullets = []
        tekibullets = []
        self.stage_number += 1
        teki_movable = self.stage_number + 1
        squad.interval = 120 - self.stage_number*6
        self.counter = 0
        
        squad.list = [
            [Teki(x*10,0,0) for x in (4,10)],
            [Teki(x*10,20,1) for x in range(2,14,2)],
            [Teki(x*10,40,2) for x in range(0,16,2)],
            [Teki(x*10,60,3) for x in range(0,16,2)],
        ]

    def update(self):
        global score

        ### ★の更新
        for star in stars:
            star.update()
            if star.y > APP_HEIGHT:
                stars.remove(star)
                stars.append(Star())

        ### ゲーム開始の判定
        if self.is_gaming == False:
            if (pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)):
                score = 0
                self.init_stage()
                self.is_gaming = True
            return
        
        
        ### ステージクリアの判定
        if sum(map(len,squad.list))==0:
            self.init_stage()
            return
            
        ### ゲームオーバーの判定
        obstacles=tekibullets+sum(squad.list,[])
        for obs in obstacles:
            if obs.check_hit(myship.x,myship.y):
                pyxel.play(2,2)
                self.init_game()
                return

        ### ステージ開始からの経過フレーム数の更新
        self.counter += 1

        ### 自機の移動判定
        myship.dir = 4   # 移動無し
        for i in range(2,4):
            if pyxel.btn(KEY[i]) or  LAXIS_RANGE[i][0] < pyxel.btnv(LAXIS[i]) < LAXIS_RANGE[i][1] or pyxel.btn(GPAD[i]): # key, analogstick, Dpad
                myship.dir = i   # 移動有り

        ### 弾発射の判定
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            bullets.append(Bullet(myship.x + 7,myship.y))
            pyxel.play(0,0)

        ### 弾の生存確認
        for bullet in bullets:
            if bullet.y < -10:
                bullets.remove(bullet)
        
        for bullet in tekibullets:
            if bullet.y > APP_HEIGHT + 10:
                tekibullets.remove(bullet)

        ### メッセージの生存確認
        for mes in messages:
            if mes.cnt < 0:
                messages.remove(mes)

        ### 自機の更新
        myship.update()
        ### 弾の更新
        for bullet in bullets:
            bullet.update()
        for bullet in tekibullets:
            bullet.update()
        ### 分隊の更新
        squad.update()
        ### 敵の更新
        for tekis in squad.list:
            for teki in tekis:
                teki.update()
        ### メッセージの更新
        for mes in messages:
            mes.update()

    def draw(self):
        pyxel.cls(0)

        for star in stars:star.draw()

        if self.is_gaming:            
            ### 自機の描画
            myship.draw()
            ### 弾の描画
            [bullet.draw() for bullet in bullets+tekibullets]
            ### 敵の描画
            [teki.draw() for tekis in squad.list for teki in tekis]
            ### メッセージの描画
            [mes.draw() for mes in messages]

            ### ステージ番号の描画
            pyxel.blt(10,10,1,0,0,40,16,0)
            pyxel.blt(60,10,1,0,self.stage_number*16+16,16,16,0)
        else:### ゲーム開始してないときの描画
            pyxel.text(200,220,"MOD 0.1",7)
            pyxel.text(82,150,"Push BUTTON to Start",pyxel.frame_count%16)

            pyxel.blt(-4,100,2,0,32,256,48,0)
            pyxel.blt(28,10,1,48,0,64,16,0)

        ### スコアの描画はUIなので最後に。
        if score >= 1000:pyxel.blt(APP_WIDTH - 8*4-10,10,1,0,score//1000%10*16+16,8,16,0)
        if score >= 100:pyxel.blt(APP_WIDTH - 8*3-10,10,1,0,score//100%10*16+16,8,16,0)
        if score >= 10:pyxel.blt(APP_WIDTH - 8*2-10,10,1,0,score//10%10*16+16,8,16,0)
        pyxel.blt(APP_WIDTH - 8*1-10,10,1,0,score%10*16+16,8,16,0)
        sc = self.hiscore
        if sc >= 1000:pyxel.blt(APP_WIDTH - 8*4-100,10,1,0,sc//1000%10*16+16,8,16,0)
        if sc >= 100:pyxel.blt(APP_WIDTH - 8*3-100,10,1,0,sc//100%10*16+16,8,16,0)
        if sc >= 10:pyxel.blt(APP_WIDTH - 8*2-100,10,1,0,sc//10%10*16+16,8,16,0)
        pyxel.blt(APP_WIDTH - 8*1-100,10,1,0,score%10*16+16,8,16,0)
    
App()