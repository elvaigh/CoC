import sys
import math
import copy
import time
import queue
import random
# To debug: print("Debug messages...", file=sys.stderr)
maxCopy=20
maxBareel=100
turnBeforMine=4
turnBeforFire=1
maxStackSize=200

BARREL = 4
mPair=[(1,0),(0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
mImp =[(1,0), (1,-1), (0,-1), (-1,0),  (0,1), (1,1)]
hexAdj=[mPair,mImp]
gameGrid = [[0 for i in range(21)] for j in range(23)]
canons = [[0 for i in range(21)] for j in range(23)]
def rddllt(x,y, radius, filter):
    lower_x = x-radius
    upper_x = x+radius
    li = []
    if (filter):
        for i in range(lower_x, upper_x+1):
            if (validee(i, y)):
                li.append((i, y))
        for i in range(1, radius):
            cur_lower_x = lower_x
            cur_upper_x = upper_x
            cur_y = y-i
            if (cur_y%2==0):
                cur_lower_x += 1
            else:
                cur_upper_x -= 1
            for j in range(cur_lower_x, cur_upper_x+1):
                if (valide(j, cur_y)):
                    li.append((j, cur_y))
                if (valide(j, y+i)):
                    li.append((j, y+i))
    else:
        for i in range(lower_x, upper_x+1):
            li.append((i, y))
        for i in range(1, radius):
            cur_lower_x = lower_x
            cur_upper_x = upper_x
            cur_y = y-i
            if (cur_y%2==0):
                cur_lower_x += 1
            else:
                cur_upper_x -= 1
            for j in range(cur_lower_x, cur_upper_x+1):
                li.append((j, cur_y))
                li.append((j, y+i))
    return li
def findBestMove(ship):
    potentialCells = rddllt(ship.position.x,ship.position.y, 3, True)
    bestScore = -999999999
    bestCell = None
    # Score surrounding cells
    for cell in potentialCells:
        score = 0
        surroundingCells = rddllt(cell[0], cell[1], 5, False)
        for surr_cell in surroundingCells:
            if (not valide(surr_cell[0], surr_cell[1])):
                score -= 1
            else:
                if (gameGrid[surr_cell[0]][surr_cell[1]] != 0):
                    score -= 10
        if (score > bestScore):
            bestScore = score
            bestCell = cell
    if (bestCell is None):
        return (11, 10)
    return bestCell
def valide(x,y):return x>=0 and x<23 and y>=0 and y<21
def bfs(sx, sy):
    q = queue.Queue()
    q.put((sx, sy))
    v = [[False for i in range(21)] for j in range(23)]
    stackConut = 0
    tgt=-100
    best=None
    while(not q.empty()):
        cur = q.get()
        cx = cur[0]
        cy = cur[1]
        if (v[cx][cy]):
            continue
        stackConut += 1
        if (stackConut > maxStackSize):
            break
        if (not valide(cx, cy)):
            continue
        if (gameGrid[cx][cy]> tgt):
            best=cur
            tgt=gameGrid[cx][cy]
        for i in range(6):
            nx = cx
            ny = cy
            nx = cx+hexAdj[cy%2][i][0]
            ny = cy+hexAdj[cy%2][i][1]
            if (not valide(nx, ny)):
                continue
            q.put((nx, ny))
        v[cx][cy] = True
    return best

# Optimizations
sys.setcheckinterval(1000000)

debug=False
class Case(object):
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.evenDir=[(1,0),(0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
        self.oddDir=[(1,0), (1,-1), (0,-1), (-1,0),  (0,1), (1,1)]
        self.e=None
    def angle(self, targetPosition):
        dy = (targetPosition.y - self.y) * math.sqrt(3) / 2
        dx = targetPosition.x - self.x + ((self.y - targetPosition.y) & 1) * 0.5
        angle = -math.atan2(dy, dx) * 3 / math.pi
        if angle < 0: angle += 6
        elif angle >=6:angle -= 6
        return int(angle)
        
    def toCubeCoordinate(self):
            xp = self.x - (self.y - (self.y & 1)) / 2
            zp = self.y
            yp = -(xp + zp)
            return  Cube(xp, yp, zp)
    def neighbor(self, orientation):
        if (self.y % 2 == 1):
                newY = self.y + self.oddDir[orientation][1]
                newX = self.x + self.oddDir[orientation][0]
        else:
                newY = self.y + self.evenDir[orientation][1]
                newX = self.x + self.evenDir[orientation][0]
        return  Case(newX, newY)
    def distanceTo(self,dst): return self.toCubeCoordinate().distanceTo(dst.toCubeCoordinate())
        
    def distance(self,e):return math.sqrt((e.x-self.x)**2+(e.y-self.y)**2)
    def __str__(self):return "{} {}".format(self.x, self.y)
    def valide(self):
        return self.x>=0 and self.x<23 and self.y>=0 and self.y<21
    def equals(self,other):return self.x==other.x and self.y==other.y
class Cube(object):
    def __init__(self,x,y,z):
        self.directions =[(1, -1, 0 ), ( +1, 0, -1 ), ( 0, +1, -1 ), ( -1, +1, 0 ), ( -1, 0, +1 ), ( 0, -1, +1 )]
        self.x,self.y,self.z=x,y,z
    def toOffsetCoordinate(self):
            newX = self.x + (self.z - (self.z & 1)) / 2
            newY = self.z
            return Case(newX, newY)
    def neighbor(self, orientation):
            nx = self.x + self.directions[orientation][0]
            ny = self.y + self.directions[orientation][1]
            nz = self.z + self.directions[orientation][2]
            return Cube(nx, ny, nz)
    def distanceTo(self,dst):return (abs(self.x - dst.x) + abs(self.y - dst.y) + abs(self.z - dst.z)) // 2
    
    
class Entity(object):
    def __init__(self,entityId,x,y):self.entityId,self.position=entityId,Case(x,y)
    def distance(self,e):return self.position.distance(e.position)
class Ship(Entity):
    def __init__(self,entityId,arg1,arg2,arg3,arg4,x,y):
        Entity.__init__(self,entityId,x,y)
        self.initialHealth=100
        self.orientation,self.speed,self.rhum,self.owner=arg1,arg2,arg3,arg4 
        self.beforeToMine=0
        self.beforeToFire=0
        self.newOrientation=0
        self.newBowCoordinate=None
        self.newSternCoordinate=None
        self.action=None
        self.target=None
        
    def  moveTo(x,y):
        currentPosition=self.position
        target=Case(x,y)
        if currentPosition.equals(targetPosition):self.action=1;return
        if self.speed==2:self.action=1
        elif self.speed==1:
            #Suppose we've moved first
            currentPosition = currentPosition.neighbor(self.orientation)
            if (not currentPosition.valide()):self.action =1;break
            #Target reached at next turn
            if (currentPosition.equals(targetPosition)):self.action = None;break
            #For each neighbor cell, find the closest to target
            targetAngle = currentPosition.angle(targetPosition)
            angleStraight = min(abs(self.orientation - targetAngle), 6 - abs(self.orientation - targetAngle))
            anglePort = min(abs((self.orientation + 1) - targetAngle), abs((self.orientation - 5) - targetAngle))
            angleStarboard = min(abs((self.orientation + 5) - targetAngle), abs((self.orientation - 1) - targetAngle))

            centerAngle = currentPosition.angle(new Coord(MAP_WIDTH / 2, MAP_HEIGHT / 2))
            anglePortCenter = min(abs((self.orientation + 1) - centerAngle), abs((self.orientation - 5) - centerAngle))
            angleStarboardCenter = min(abs((self.orientation + 5) - centerAngle), abs((self.orientation - 1) - centerAngle))
            #Next to target with bad angle, slow down then rotate (avoid to turn around the target!)
            if (currentPosition.distanceTo(targetPosition) == 1 and angleStraight > 1.5):self.action = 1;break

            distanceMin = None
            # Test forward
            nextPosition = currentPosition.neighbor(self.orientation)
            if (nextPosition.valide()):distanceMin = nextPosition.distanceTo(targetPosition);self.action =None
            #Test port
            nextPosition = currentPosition.neighbor((self.orientation + 1) % 6)
            if (nextPosition.valide()):
                distance = nextPosition.distanceTo(targetPosition)
                if (distanceMin == None or distance < distanceMin or distance == distanceMin and anglePort < angleStraight - 0.5):
                    distanceMin = distance
                    self.action = 2
                    break
            #Test starboard
            nextPosition = currentPosition.neighbor((self.orientation + 5) % 6)
            if (nextPosition.valide()):
                distance = nextPosition.distanceTo(targetPosition)
                if (distanceMin == None or distance < distanceMin
                        or (distance == distanceMin and angleStarboard < anglePort - 0.5 and self.action ==2)
                        or (distance == distanceMin and angleStarboard < angleStraight - 0.5 and self.action == None)
                        or (distance == distanceMin and self.action == 2 and angleStarboard == anglePort
                                and angleStarboardCenter < anglePortCenter)
                        or (distance == distanceMin and self.action == 2 and angleStarboard == anglePort
                                and angleStarboardCenter == anglePortCenter and (self.orientation == 1 or self.orientation == 4))):
                    distanceMin = distance
                    self.action = 3
                    break
        elif self.speed==1:
            #Rotate ship towards target
            targetAngle = currentPosition.angle(targetPosition)
            angleStraight = min(abs(self.orientation - targetAngle), 6 - abs(self.orientation - targetAngle))
            anglePort = min(abs((self.orientation + 1) - targetAngle), abs((self.orientation - 5) - targetAngle))
            angleStarboard = min(abs((self.orientation + 5) - targetAngle), abs((self.orientation - 1) - targetAngle))

            centerAngle = currentPosition.angle(new Coord(MAP_WIDTH / 2, MAP_HEIGHT / 2))
            anglePortCenter = min(abs((self.orientation + 1) - centerAngle), abs((self.orientation - 5) - centerAngle))
            angleStarboardCenter = min(abs((self.orientation + 5) - centerAngle), abs((self.orientation - 1) - centerAngle))
            forwardPosition = currentPosition.neighbor(self.orientation)
            self.action = None

            if (anglePort <= angleStarboard):self.action = 2
          
            if (angleStarboard < anglePort or angleStarboard == anglePort and angleStarboardCenter < anglePortCenter
                    or angleStarboard == anglePort and angleStarboardCenter == anglePortCenter and (self.orientation == 1 or self.orientation == 4)):self.action =3
        
            if (forwardPosition.valide() and angleStraight <= anglePort and angleStraight <= angleStarboard):self.action =3
            break

    def faster(self):self.action = 0
    def slower(self) :self.action = 1
    def port(self):self.action =2
    def starboard(self)self.action =3
    def placeMine(self):self.action = 4
    def stern(self) : return self.position.neighbor((self.orientation + 3) % 6)
    def bow(self):return self.position.neighbor(self.orientation)
    def newStern(self):self.position.neighbor((self.newOrientation + 3) % 6)
    def newBow(self):return self.position.neighbor(self.newOrientation)
    def fire(self,x,y):self.target = Coord(x, y);self.action = 5
    def heal(self, health):
        self.rhum+=health
        if (self.rhum > 100):self.rhum = 100
    def newPositionsIntersect(self, other):
        sternCollision = self.newSternCoordinate != None and (self.newSternCoordinate.equals(other.newBowCoordinate)or self.newSternCoordinate.equals(other.newPosition) or self.newSternCoordinate.equals(other.newSternCoordinate))
        centerCollision =self.newPosition != None and (self.newPosition.equals(other.newBowCoordinate) or newPosition.equals(other.newPosition)or self.newPosition.equals(other.newSternCoordinate))
        return newBowIntersect(other) or sternCollision or centerCollision
    def newPositionsIntersect(self,ships):
        for other in ships:
            if (self != other && self.newPositionsIntersect(other)):return true
        return false
    def damage(self, health):
        self.rhum -= health
        if (self.rhum <= 0):self.rhum= 0

    '''def fire(self,ships):
        global gameGrid
        if self.beforeToFire!=0:self.updateFire();return None
        for s in ships:
                c=s.position
                d=self.position.distanceTo(c)
                tours=round((d+1)//3)    
                for i in range(tours*s.speed):c=c.neighbor(s.orientation)
                d=c.distanceTo(self.position)
                if d<=10 and c.valide():self.beforeToFire=1;gameGrid[c.x][c.y]=50;return Fire(c.x,c.y)
        return None'''

class Damage(object):
    def __init__(self,position,health,hit):self.position,self.health,self.hit=position,health,hit

class Barrel(Entity):
    def __init__(self,entityId,arg1,x,y):Entity.__init__(self,entityId,x,y);self.rhum=arg1

class Mine(Entity):
    def __init__(self,entityId,x,y):Entity.__init__(self,entityId,x,y)
    def explode(self,ships, force):
        damage = []
        victim = None

        for ship in ships:
            if position.equals(ship.bow()) or position.equals(ship.stern()) or position.equals(ship.position):
            damage +=[Damage(self.position, 25, True)]
            ship.damage(25)
            victim = ship

        if (force or victim != None):
            if (victim == None):damage +=[Damage(self.position, 25, True)]
            for ship in ships:
                if (ship != victim) :
                    impactPosition = None
                    if (ship.stern().distanceTo(position) <= 1):impactPosition = ship.stern()
                    if (ship.bow().distanceTo(position) <= 1):impactPosition = ship.bow();
                    if (ship.position.distanceTo(position) <= 1):impactPosition = ship.position
                    if (impactPosition != null):
                        ship.damage(10)
                        damage +=[Damage(impactPositionn, 10, True)]

        return damage

class Cannoball(Entity):
    def __init__(self,entityId,x,y,arg1,arg2):Entity.__init__(self,entityId,x,y);self.owner,self.remainingTurns=arg1,arg2
class Ation(object):
    def __init__(self,x,y):self.x,self.y=x,y
class Move(Ation):
     def __init__(self,x,y):ACTION.__init__(self,x,y)
     def __str__(self):return "MOVE {} {}".format(self.x, self.y)
     def utility(self,player):return maxBareel-payer.ships[-1].rhum+1
     
class Fire(Ation):
     def __init__(self,x,y):ACTION.__init__(self,x,y)
     def __str__(self):return "FIRE {} {}".format(self.x, self.y)
     def utility(self):return 1
class Port(Ation):
    def __init__(self,x,y):ACTION.__init__(self,x,y)
    def __str__(self):return "PORT"
    
class Starboard(Ation):
    def __init__(self,x,y):ACTION.__init__(self,x,y)
    def __str__(self):return "Starboard"
    
class Faster(Ation):
    def __init__(self,x,y):ACTION.__init__(self,x,y)
    def __str__(self):return "Faster"

class Slower(Ation):
    def __init__(self,x,y):ACTION.__init__(self,x,y)
    def __str__(self):return "Slower"
    
class Wait(Ation):
    def __init__(self,x,y):ACTION.__init__(self,x,y)
    def __str__(self):return "Wait"
class Mine(Wait):
    def __init__(self,x,y):Wait.__init__(self,x,y)
    def __str__(self):return "MINE"
        
class Player(object):
    
    def __init__(self,player,ships):self.player,self.ships=player,ships
    def play(self,game):
        actions=[]
        global gameGrid
        for s in self.ships:
             actions=[s.fire(game.players[0].ships)]+[s.move(game.barrels)]+[s.slower()]+[s.faster()]+[s.starboard()]+[s.port()]+[s.mine()]
             tmp=-50
             mm=MOVE(11,10)
             for a in actions:
                 if a and gameGrid[a.x][a.y]>tmp:mm=a;tmp=gameGrid[a.x][a.y]
             print(mm)
             
class Game(object):
    def __init__(self):
        self.players,self.mines,self.barrels,self.cannonballs=[],[],[],[]
        self.cannonBallExplosions=[]
        self.damage=[]
        self.turn=0
    def updateInput(self):
        global gameGrid
        gameGrid=[[0 for i in range(21)] for j in range(23)]
        self.mines,self.barrels,self.cannonballs,self.players=[],[],[],[Player(0,[]),Player(1,[])]
        my_ship_count = int(input())  # the number of remaining ships
        entity_count = int(input())  # the number of entities (e.g. ships, mines or cannonballs)
        for i in range(entity_count):
            entity_id, entityType, x, y, arg_1, arg_2, arg_3, arg_4 = input().split()
            entity_id = int(entity_id)
            x = int(x)
            y = int(y)
            arg_1 = int(arg_1)
            arg_2 = int(arg_2)
            arg_3 = int(arg_3)
            arg_4 = int(arg_4)
            if entityType =='SHIP':self.players[arg_4].ships+=[Ship(entity_id,arg_1, arg_2, arg_3, arg_4,x,y)];gameGrid[x][y]=1-arg_4
            elif entityType =='BARREL':self.barrels+=[Barrel(entity_id,arg_1,x,y)];gameGrid[x][y]=arg_1
            elif entityType =='CANNONBALL':
                self.cannonballs+=[Cannoball(entity_id,arg_1, arg_2,x,y)]
                if arg_2<=1:gameGrid[x][y]=-50
            elif entityType =='MINE':self.mines+=[Mine(entity_id,x,y)];gameGrid[x][y]=-25
        self.turn+=1
    def decrementRum(self):
        ships=self.players[0].ships+self.players[1].ships
        for ship in self.ships:ship.damage(1)
    def void updateInitialRum(self):
        ships=self.players[0].ships+self.players[1].ships
        for ship in ships:
            ship.initialHealth = ship.rhum
    def moveCannonballs(self):
        for ball in self.cannonballs:
            if (ball.remainingTurns == 0):del canon;continue
            else if (ball.remainingTurns > 0):ball.remainingTurns--
            if (ball.remainingTurns == 0):self.cannonBallExplosions+=[ball.position]
    def checkBarrelCollisions(self, ship):
        bow = ship.bow()
        stern = ship.stern()
        center = ship.position
        for barrel in self.barrels:
            if (barrel.position.equals(bow) or barrel.position.equals(stern) or barrel.position.equals(center)):ship.heal(barrel.rhum);del barrel
    def checkMineCollisions(self):
        ships=self.players[0].ships+self.players[1].ships
        for min in self.mines:
            mineDamage = mine.explode(ships, False)
            if len(mineDamage)>0:damage+=mineDamage
    def checkCollisions(self):
        ships=self.players[0].ships+self.players[1].ships
        # Check collisions with Barrels
        for ship in ships:checkBarrelCollisions(ship)
        # Check collisions with Mines
        checkMineCollisions()

    def moveShips(self):
        ships=self.players[0].ships+self.players[1].ships
        for  i in range(1,3):
            for ship in ships:
                ship.newPosition = ship.position
                ship.newBowCoordinate = ship.bow()
                ship.newSternCoordinate = ship.stern()
                if (i > ship.speed):continue
                newCoordinate = ship.position.neighbor(ship.orientation)
                if (newCoordinate.valide()):
                    # Set new coordinate.
                    ship.newPosition = newCoordinate
                    ship.newBowCoordinate = newCoordinate.neighbor(ship.orientation)
                    ship.newSternCoordinate = newCoordinate.neighbor((ship.orientation + 3) % 6)
                else:
                    #Stop ship!
                    ship.speed = 0

            #Check ship and obstacles collisions
            collisions = []
            collisionDetected = true
            while (collisionDetected):
                collisionDetected = false
                for (Ship ship : this.ships):
                    if (ship.newBowIntersect(ships)):collisions.add(ship)

                for ship in collisions:
                    # Revert last move
                    ship.newPosition = ship.position
                    ship.newBowCoordinate = ship.bow()
                    ship.newSternCoordinate = ship.stern()
                    ship.speed = 0
                    collisionDetected = true
                
                collisions=[]
                #Move ships to their new location
                for ship in ships : ship.position = ship.newPosition
            self.checkCollisions()
    def rotateShips(self):
        ships=self.players[0].ships+self.players[1].ships
        #Rotate
        for  ship in ships:
            ship.newPosition = ship.position
            ship.newBowCoordinate = ship.newBow()
            ship.newSternCoordinate = ship.newStern()
        #Check collisions
        collisionDetected = true
        collisions =[]
        while (collisionDetected):
            collisionDetected = false
            for ship in ships:
                if (ship.newPositionsIntersect(ships)):collisions+=[ship]
            for ship in collisions:
            ship.newOrientation = ship.orientation
            ship.newBowCoordinate = ship.newBow()
            ship.newSternCoordinate = ship.newStern()
            ship.speed = 0
            collisionDetected = true
            collisions=[]
        #Apply rotation
        forship in ships:ship.orientation = ship.newOrientation
        self.checkCollisions()

    def gameIsOver(self):
        for player in self.players: 
            if len(self.player.ships)==0:return True
        return len(self.barrels) == 0 and self.turn==200

    def explodeShips(self):
        ships=self.players[0].ships+self.players[1].ships
        for position in self cannonBallExplosions:
            for ship in ships:
                if (position.equals(ship.bow()) or position.equals(ship.stern())):
                    self.damage+=[Damage(position, 25, True)]
                    ship.damage(25)
                    del position
                    break
                else if (position.equals(ship.position)):
                    self.damage+=[Damage(position, 25, True)]
                    ship.damage(50)
                    del position
                    break
    def explodeMines(self):
        ships=self.players[0].ships+self.players[1].ships
        for ball in self.cannonBallExplosions:
            for mine in self.mines:
                if (mine.position.equals(ball)):
                    self.damage+=mine.explode(ships, True)
                    del mine
                    del ball
                    break
    def explodeBarrels(self):
        for ball in self.cannonBallExplosions:
            for Barrel in self.barrels:
                if (barrel.position.equals(position)):
                    self.damage+=[Damage(position, 0, True)]
                    del ball
                    del bareel
                    break
    def updateGame(self):
        self.moveCannonballs()
        self.decrementRum()
        self.updateInitialRum()

        self.applyActions()
        self.moveShips()
        self.rotateShips()

        self.explodeShips()
        self.explodeMines()
        self.explodeBarrels()

        #For each sunk ship, create a new rum barrel with the amount of rum the ship had at the begin of the turn (up to 30).
        for ship in ships:
            if (ship.health <= 0):
                reward = min(30, ship.initialHealth)
                if (reward > 0):self.barrels+=[Barrel(ship.position.x, ship.position.y, reward)];del ship
       
        for position in cannonBallExplosions:damage+=[Damage(position, 0, True)]
           

    
    def applyActions(self):
        for p in self.players:
            for ship in p.ships:
                if ship.beforeToMine>0:ship.beforeToMine-=1
                if ship.beforeToFire>0:ship.beforeToFire-=1
                ship.newOrientation = ship.orientation
                if (ship.action != None):
                    if ship.action==0:
                        if (ship.speed < 2):ship.speed+=1
                    elif ship.action==1:
                        if (ship.speed >0):ship.speed-=1
                    elif ship.action==2:ship.newOrientation = (ship.orientation + 1) % 6
                    elif ship.action==3:ship.newOrientation = (ship.orientation + 3) % 6
                elif ship.action==4:
                     if (ship.beforeToMine == 0):
                        target = ship.stern().neighbor((ship.orientation + 3) % 6)
                        if (target.valide()):
                            cellIsFreeOfBarrels =self.barrels.stream().noneMatch(barrel -> barrel.position.equals(target))
                            cellIsFreeOfMines = self.mines.stream().noneMatch(mine -> mine.position.equals(target))
                            cellIsFreeOfShips = self.ships.stream().filter(b -> b != ship).noneMatch(b -> b.at(target))
                            if (cellIsFreeOfBarrels and  cellIsFreeOfShips and cellIsFreeOfMines):
                                ship.beforeToMine = 5
                                self.mines+=[Mine(target.x, target.y)]
                elif ship.action==5:
                    distance = ship.bow().distanceTo(ship.target)
                    if (ship.target.valide() and distance <= 10 and ship.beforeToFire == 0):
                        travelTime = (int) (1 + round(ship.bow().distanceTo(ship.target) / 3.0))
                        cannonballs+=[Cannonball(ship.target.x, ship.target.y, ship.id, ship.bow().x, ship.bow().y, travelTime)]
                        ship.beforeToFire=2
    def clone(self): 
        g=Game()
        g.players=copy.copy(self.players)    
        g.turn=copy.copy(self.turn)
        g.barrels=copy.copy(self.barrels)
        g.cannonBallExplosions=copy.copy(self.cannonBallExplosions)
        g.mines=copy.copy(self.mines) 
        g.damage=copy.copy(self.damage)          
  
g=Game()
# game loop
while True:
    time_t = time.time()
    g.updateInput()
    g.players[-1].play(g)
    time_t = time.time()-time_t
    print("Debug messages...",time_t, file=sys.stderr)