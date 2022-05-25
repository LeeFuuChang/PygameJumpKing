from sre_constants import JUMP
from .functions import *
from .collision import *
from .constants import *
from .vector import *
from .shapes import *

class Player:
    runCycleIdx = 0
    runCycle = (
        [PLAYER_RUN_IMAGE_1]*6 +
        [PLAYER_RUN_IMAGE_2]*6 +
        [PLAYER_RUN_IMAGE_3]*6 +
        [PLAYER_RUN_IMAGE_3]*6 +
        [PLAYER_RUN_IMAGE_2]*6 +
        [PLAYER_RUN_IMAGE_1]*6
    )
    def __init__(self):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.velx = 0
        self.vely = 0
        self.pvelx = 0
        self.pvely = 0

        self.jumpTimer = 0

        self.jumpStartHeight = 0

        self.currentLevelNo = 0

        self.isOnGround = True
        self.isRunning = False
        self.isSliding = False
        self.isSlidingLeft = False
        self.hasBumped = False
        self.hasFallen = False

        self.facingRight = True

        self.jumpHeld = False
        self.leftHeld = False
        self.rightHeld = False




    def isPlayerOnGround(self, currentLines):
        self.y += 1
        for line in currentLines:
            if not line.isHorizontal: continue
            if self.CheckCollideWithLine(line):
                self.y -= 1
                return True
        self.y -= 1
        return False


    def isPlayerOnDiagonal(self, currentLines):
        self.y += 5
        for line in currentLines:
            if not line.isDiagonal: continue
            if self.CheckCollideWithLine(line):
                self.y -= 5
                return True
        self.y -= 5
        return False


    def isMovingLeft(self):
        return self.velx < 0


    def isMovingRight(self):
        return self.velx > 0


    def isMovingUp(self):
        return self.vely < 0


    def isMovingDown(self):
        return self.vely > 0





    def CheckCollideWithLine(self, line):
        if line.isHorizontal:
            onX = (
                line.x1 < self.x and self.x < line.x2
            ) or (
                line.x1 < self.x+self.w and self.x+self.w < line.x2
            ) or (
                self.x < line.x1 and line.x1 < self.x+self.w 
            ) or (
                self.x < line.x2 and line.x2 < self.x+self.w
            )
            onY = self.y < line.y1 and line.y1 < self.y+self.h
            return onX and onY
        elif line.isVertical:
            onY = (
                line.y1 < self.y and self.y < line.y2
            ) or (
                line.y1 < self.y+self.h and self.y+self.h < line.y2
            ) or (
                self.y < line.y1 and line.y1 < self.y+self.h 
            ) or (
                self.y < line.y2 and line.y2 < self.y+self.h
            )
            onX = self.x < line.x1 and line.x1 < self.x+self.w
            return onX and onY
        else:
            tl = Point(self.x, self.y)
            tr = Point(tl.x+self.w, tl.y)
            bl = Point(tl.x, tl.y+self.h-1) # -1 to let player float on ground so we wont fell into infinite collision
            br = Point(tr.x, tr.y+self.h-1)

            lCollided = CheckLinesCollision(tl, bl, line.p1, line.p2)
            rCollided = CheckLinesCollision(tr, br, line.p1, line.p2)
            tCollided = CheckLinesCollision(tl, tr, line.p1, line.p2)
            bCollided = CheckLinesCollision(bl, br, line.p1, line.p2)

            if lCollided[0] or rCollided[0] or tCollided[0] or bCollided[0]:
                cInfo = DiagonalCollisionInfo()
                cInfo.collidePlayerL = lCollided[0]
                cInfo.collidePlayerR = rCollided[0]
                cInfo.collidePlayerT = tCollided[0]
                cInfo.collidePlayerB = bCollided[0]

                if lCollided[0]:
                    cInfo.collisionPoints.append(Point(lCollided[1], lCollided[2]))
                if rCollided[0]:
                    cInfo.collisionPoints.append(Point(rCollided[1], rCollided[2]))
                if tCollided[0]:
                    cInfo.collisionPoints.append(Point(tCollided[1], tCollided[2]))
                if bCollided[0]:
                    cInfo.collisionPoints.append(Point(bCollided[1], bCollided[2]))
                line.SetDiagonalCollisionInfo(cInfo)
                return True
            else:
                return False


    def GetPriorityCollision(self, collidedLines):
        if len(collidedLines) == 2:
            vert = None
            hori = None
            diag = None
            if collidedLines[0].isVertical: vert = collidedLines[0]
            if collidedLines[0].isHorizontal: hori = collidedLines[0]
            if collidedLines[0].isDiagonal: diag = collidedLines[0]
            if collidedLines[1].isVertical: vert = collidedLines[1]
            if collidedLines[1].isHorizontal: hori = collidedLines[1]
            if collidedLines[1].isDiagonal: diag = collidedLines[1]

            if vert is not None and hori is not None:
                if self.isMovingUp():
                    if vert.center.y > hori.center.y:
                        return vert
                    else:
                        return hori
                else:
                    if vert.center.y < hori.center.y:
                        return vert
                    else:
                        return hori
            if hori is not None and diag is not None:
                if diag.center.y > hori.center.y:
                    return hori

        maxXCorrectionAllowed = -self.velx
        maxYCorrectionAllowed = -self.vely
        minCorrection = WIDTH*HEIGHT
        chosenLine = None
        for line in collidedLines:
            if line.isHorizontal:
                if self.isMovingDown():
                    vector = Vector(0, line.y1 - (self.y+self.h))
                    correction = abs( line.y1 - (self.y+self.h) )
                else:
                    vector = Vector(0, line.y1 - self.y)
                    correction = abs( line.y1 - self.y )
            elif line.isVertical:
                if self.isMovingRight():
                    vector = Vector(line.x1 - (self.x+self.w), 0)
                    correction = abs( line.x1 - (self.x+self.w) )
                else:
                    vector = Vector(line.x1 - self.x, 0)
                    correction = abs( line.x1 - self.x )
            else:
                if len(line.diagonalCollisionInfo.collisionPoints)==1:
                    if line.diagonalCollisionInfo.collidePlayerT:
                        vector = Vector(0, max(line.y1, line.y2) - self.y)
                        correction = abs( vector.y )
                    if line.diagonalCollisionInfo.collidePlayerB:
                        vector = Vector(0, min(line.y1, line.y2) - (self.y+self.h))
                        correction = abs( vector.y )
                    if line.diagonalCollisionInfo.collidePlayerL:
                        vector = Vector(0, max(line.x1, line.x2) - self.x)
                        correction = abs( vector.x )
                    if line.diagonalCollisionInfo.collidePlayerR:
                        vector = Vector(0, min(line.x1, line.x2) - (self.x+self.w))
                        correction = abs( vector.x )
                else:
                    pa, pb = line.diagonalCollisionInfo.collisionPoints[:2]
                    center = Point( (pa.x+pb.x)/2, (pa.y+pb.y)/2 )
                    cT = line.diagonalCollisionInfo.collidePlayerT
                    cB = line.diagonalCollisionInfo.collidePlayerB
                    cL = line.diagonalCollisionInfo.collidePlayerL
                    cR = line.diagonalCollisionInfo.collidePlayerR
                    if   cT and cL: 
                        playerCollidedCorner = Point(self.x       , self.y       )
                    elif cT and cR: 
                        playerCollidedCorner = Point(self.x+self.w, self.y       )
                    elif cB and cL: 
                        playerCollidedCorner = Point(self.x       , self.y+self.h)
                    elif cB and cR: 
                        playerCollidedCorner = Point(self.x+self.w, self.y+self.h)
                    else:
                        pccX = self.x+(int(self.isMovingRight())*self.w)
                        pccY = self.y+(int(self.isMovingDown())*self.h)
                        playerCollidedCorner = Point(pccX, pccY)
                    vector = Vector( center.x - playerCollidedCorner.x, center.y - playerCollidedCorner.y )
                    correction = dist(center.x, center.y, playerCollidedCorner.x, playerCollidedCorner.y)
            if correction < minCorrection:
                minCorrection = correction
                chosenLine = line
        return chosenLine


    def CheckCollisions(self, lines):
        collidedLines = []
        for line in lines:
            if self.CheckCollideWithLine(line):
                collidedLines.append(line)
        line = self.GetPriorityCollision(collidedLines)
        if not line: return

        potentialLanding = False
        if line.isHorizontal:
            if self.isMovingDown():
                self.y = line.y1 - self.h
                if len(collidedLines) > 1:
                    potentialLanding = True
                    self.velx, self.vely = 0, 0
                else:
                    self.Land()
            else:
                self.vely = -self.vely/2
                self.y = line.y1
        elif line.isVertical:
            if self.isMovingRight():
                self.x = line.x1 - self.w
            elif self.isMovingLeft():
                self.x = line.x1
            else:
                if self.pvelx > 0:
                    self.x = line.x1 - self.w
                else:
                    self.x = line.x1
            self.velx = -self.velx/2
            if not self.isOnGround:
                self.hasBumped = True
        else:
            self.isSliding = True
            self.hasBumped = True
            if len(line.diagonalCollisionInfo.collisionPoints)==1:
                if line.diagonalCollisionInfo.collidePlayerT:
                    self.y = max(line.y1, line.y2)+1
                    self.vely = -self.vely/2
                if line.diagonalCollisionInfo.collidePlayerB:
                    self.isOnGround = True
                    self.y = min(line.y1, line.y2)-self.h-1
                    self.velx, self.vely = 0, 0
                if line.diagonalCollisionInfo.collidePlayerL:
                    self.x = max(line.x1, line.x2)+1
                    if self.isMovingLeft():
                        self.velx = -self.velx/2
                    if not self.isOnGround: self.hasBumped = True
                if line.diagonalCollisionInfo.collidePlayerR:
                    self.x = min(line.x1, line.x2)-self.w-1
                    if self.isMovingRight():
                        self.velx = -self.velx/2
                    if not self.isOnGround: self.hasBumped = True
            else:
                pa, pb = line.diagonalCollisionInfo.collisionPoints[:2]
                center = Point( (pa.x+pb.x)/2, (pa.y+pb.y)/2 )
                cT = line.diagonalCollisionInfo.collidePlayerT
                cB = line.diagonalCollisionInfo.collidePlayerB
                cL = line.diagonalCollisionInfo.collidePlayerL
                cR = line.diagonalCollisionInfo.collidePlayerR
                if   cT and cL: 
                    playerCollidedCorner = Point(self.x       , self.y       )
                elif cT and cR: 
                    playerCollidedCorner = Point(self.x+self.w, self.y       )
                elif cB and cL: 
                    playerCollidedCorner = Point(self.x       , self.y+self.h)
                    self.isSlidingLeft = False
                elif cB and cR: 
                    playerCollidedCorner = Point(self.x+self.w, self.y+self.h)
                    self.isSlidingLeft = True
                else:
                    pccX = self.x+(int(self.isMovingRight())*self.w)
                    pccY = self.y+(int(self.isMovingDown())*self.h)
                    playerCollidedCorner = Point(pccX, pccY)

                self.x += center.x - playerCollidedCorner.x
                self.y += center.y - playerCollidedCorner.y

                lineVector = Vector( line.x2-line.x1, line.y2-line.y1 )
                lineVector = VectorNormalize(lineVector)

                speedMagnitude = VectorDot(Vector(self.velx, self.vely), lineVector)

                self.velx, self.vely = VectorMult(lineVector, speedMagnitude)

                if cT:
                    self.velx, self.vely = 0, 0
                    self.isSliding = False

        if len(collidedLines)>1:
            if potentialLanding:
                if self.isPlayerOnGround(lines):
                    self.Land()


    def CheckForLevelChange(self):
        if self.y < -self.h:
            self.currentLevelNo += 1
            self.y += HEIGHT
        elif self.y > HEIGHT-self.h:
            self.currentLevelNo -= 1
            self.y -= HEIGHT
        




    def ApplyGravity(self):
        if self.isOnGround:
            self.vely = 0
            return
        elif self.isSliding:
            self.vely = min(self.vely + GRAVITY*0.5, TERMINAL_VELOCITY*0.5)
            if self.isSlidingLeft:
                self.velx = max(self.velx - GRAVITY*0.5, -TERMINAL_VELOCITY*0.5)
            else:
                self.velx = min(self.velx + GRAVITY*0.5, TERMINAL_VELOCITY*0.5)
        else:
            self.vely = min(self.vely + GRAVITY, TERMINAL_VELOCITY)





    def Jump(self):
        if not self.isOnGround: return
        verticalJumpSpeed = mapNumber(self.jumpTimer, 0, MAX_JUMP_TIMER, MIN_JUMP_SPEED, MAX_JUMP_SPEED)
        self.vely = -verticalJumpSpeed
        if self.leftHeld:
            self.velx = -JUMP_SPEED_HORIZONTAL
        elif self.rightHeld:
            self.velx = JUMP_SPEED_HORIZONTAL
        else:
            self.velx = 0
        self.hasFallen = False
        self.isOnGround = False
        self.jumpTimer = 0
        self.jumpStartHeight = (HEIGHT - self.y) + HEIGHT * self.currentLevelNo


    def Land(self):
        self.isOnGround = True
        self.isSliding = False
        self.hasBumped = False
        self.hasFallen = False
        if (self.jumpStartHeight - HEIGHT / 2 > (HEIGHT - self.y) + HEIGHT * self.currentLevelNo):
            self.hasFallen = True





    def UpdatePlayerSlide(self, lines):
        if self.isSliding:
            if not self.isPlayerOnDiagonal(lines):
                self.isSliding = False


    def UpdatePlayerRun(self, lines):
        self.isRunning = False
        if self.isOnGround:
            if not self.isPlayerOnGround(lines):
                self.isOnGround = False
                return
            if self.jumpHeld:
                self.velx = 0
                self.vely = 0
            else:
                if self.rightHeld:
                    self.hasFallen = False
                    self.isRunning = True
                    self.facingRight = True
                    self.velx = RUN_SPEED
                    self.vely = 0
                elif self.leftHeld:
                    self.hasFallen = False
                    self.isRunning = True
                    self.facingRight = False
                    self.velx = -RUN_SPEED
                    self.vely = 0
                else:
                    self.velx = 0
                    self.vely = 0


    def UpdatePlayerJump(self):
        if not self.jumpHeld and self.jumpTimer>0:
            self.Jump()


    def UpdateJumpTimer(self):
        if self.isOnGround and self.jumpHeld and self.jumpTimer < MAX_JUMP_TIMER:
            self.jumpTimer += 1


    def Update(self, currentLines):
        self.UpdatePlayerSlide(currentLines)
        self.ApplyGravity()
        self.UpdatePlayerRun(currentLines)
        self.UpdatePlayerJump()

        self.x += self.velx
        self.y += self.vely

        self.pvelx = self.velx
        self.pvely = self.vely

        self.CheckCollisions(currentLines)
        self.UpdateJumpTimer()
        self.CheckForLevelChange()





    def GetSpriteToDraw(self):
        if self.jumpHeld and self.isOnGround: return PLAYER_SQUAT_IMAGE
        if self.hasFallen: return PLAYER_FALLEN_IMAGE
        if self.hasBumped: return PLAYER_BUMP_IMAGE
        if self.vely < 0: return PLAYER_JUMP_IMAGE
        if self.isRunning:
            self.runCycleIdx = (self.runCycleIdx+1)%len(self.runCycle)
            return self.runCycle[self.runCycleIdx]
        if self.isOnGround: return PLAYER_IDLE_IMAGE
        return PLAYER_FALL_IMAGE



    def Draw(self, window):
        img = self.GetSpriteToDraw()
        imgW, imgH = img.get_size()
        img = pygame.transform.flip(img, not self.facingRight, False)
        window.blit(img, ( self.x+(self.w/2)-(imgW/2) , self.y+self.h-imgH))