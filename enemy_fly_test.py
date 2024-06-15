import pyxel , math

debugdisp=0

APP_WIDTH = 480
APP_HEIGHT = 640
CHAR_SIZE=16 



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


import math

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
            if len(self.trajectory) > 0:
                tx, ty = self.trajectory[0]
                if self.move(tx, ty):
                    self.trajectory.pop(0)

                # Adjust bullet shoot range
                if 100 - App.stage_number < self.y < 104 + App.stage_number:
                    App.tekibullets.append(TekiBullet(self.x - 16 + pyxel.rndi(0, 16), self.y + 16, (self.dx * pyxel.rndf(1, 2)) / 4))

                # Teleport enemy to top of the screen if out of screen
                if APP_HEIGHT + 32 < self.y:
                    self.is_return = True
                    self.y = -CHAR_SIZE * 2
                    self.x = APP_WIDTH / 2
                    App.flyable_enemy_count += 1

        else:
            self.x = enemy_group.x + self.rposx
            self.y = enemy_group.y + self.rposy

    def draw(self):
        u = self.is_flying and 2 + (0 < self.dx) or (self.cnt // 30) % 2
        v = self.num + 3
        pyxel.blt(self.x, self.y, 0, u * 16, v * 16, 16, 16, 0)

        if debugdisp and self.is_flying:
            pyxel.text(self.x, self.y + 16, f'{int(self.x)},{int(self.y)}', 7)
            for p1, p2 in zip(self.trajectory, self.trajectory[1:]):
                pyxel.line(p1[0], p1[1], p2[0], p2[1], 7)

    def fly(self):
        self.is_flying = True
        px = self.x +50
        py = self.y +1000

        # Generate smooth trajectory through given points
        self.trajectory = self.generate_smooth_trajectory(px, py)

        self.dy = -1  # Example direction adjustment

    def generate_smooth_trajectory(self, px, py):
        # Generate smooth trajectory passing through given points
        trajectory = []
        num_points = 10  # Number of points for interpolation
        for i in range(num_points):
            t = (i + 1) / (num_points + 1)
            tx = (1 - t) ** 3 * self.x + 3 * (1 - t) ** 2 * t * (px / 2) + 3 * (1 - t) * t ** 2 * px + t ** 3 * (APP_WIDTH / 2)
            ty = (1 - t) ** 3 * self.y + 3 * (1 - t) ** 2 * t * (py / 2) + 3 * (1 - t) * t ** 2 * py + t ** 3 * (APP_HEIGHT + 64)
            trajectory.append([tx, ty])
        return trajectory


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


class TekiBullet(BulletBase):
    def __init__(self, x, y, dx) -> None:
        super().__init__(x, y, dx=dx, dy=1, h=8, c=7)
    
    def check_hit(self, shipx, shipy):
        return self.x - CHAR_SIZE + 2 < shipx < self.x - 2 and self.y - CHAR_SIZE + 2 < shipy < self.y - 2



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

        self.init_game()
        pyxel.run(self.update,self.draw)

    def init_game(self):
        App.stage_number=0

        if App.score > self.hiscore:
            self.hiscore = App.score
            with open("hiscore.txt","w") as f:f.write(f'{self.hiscore}')

    def init_stage(self):
        App.bullet_list = []# need to empty otherwise, instant death could happen
        App.tekibullets = []# need to empty otherwise, instant death could happen
        App.stage_number += 1
        App.flyable_enemy_count = App.stage_number + 1 # simultaneous fly increases
        self.counter = 0
        MAX_COL_NUM=16*2
        enemy_group.list = [[Teki(x*10,i*20,i)for x in R] for i, R in enumerate( [(4+3*2,10+5*2),range(2,MAX_COL_NUM-2,2)]+[range(0,MAX_COL_NUM,2)]*5 )]

    def update(self):

        ### ステージクリアの判定
        if sum(map(len,enemy_group.list))==0:
            self.init_stage()
            return


        ### 弾の生存確認
        [App.bullet_list.remove(bullet)for bullet in App.bullet_list if bullet.y < -10]
        [App.tekibullets.remove(bullet) for bullet in App.tekibullets if bullet.y > APP_HEIGHT + 10]

        [bullet.update() for bullet in App.bullet_list+App.tekibullets]             # 弾の更新
        enemy_group.update()                                                # 分隊の更新
        [teki.update() for tekis in enemy_group.list for teki in tekis]     # 敵の更新    

    def draw(self):
        pyxel.cls(0)

        # core contents
        if 1:            
            [teki.draw() for tekis in enemy_group.list for teki in tekis]   # 敵の描画
            [bullet.draw() for bullet in App.bullet_list+App.tekibullets]           # 弾の描画

App()