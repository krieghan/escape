import sys
import time

from OpenGL import GL, GLU, GLUT
from game_common import interfaces
from zope.interface import implementer, verify

from escape import agents, render, fleets


@implementer(interfaces.IWorld)
class EscapeWorld(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.max_left = 0
        self.max_right = width
        self.max_bottom = 0
        self.max_top = height

        self.current_time = 0

        self.jumpPoint = agents.Stationary(position=(90000, 90000),
                                           length=100,
                                           width=100,
                                           render=render.drawJumpPoint,
                                           color=(1, 1, 1))
        
        self.escapingFleet = fleets.createEscapingFleet(world=self)
        self.pursuingFleet = fleets.createPursuingFleet(world=self)
        
        self.escapingFleet.setEnemyFleet(self.pursuingFleet)
        self.pursuingFleet.setEnemyFleet(self.escapingFleet)
        
        escapingMotherShip = self.escapingFleet.getMotherShip()
        pursuingMotherShip = self.pursuingFleet.getMotherShip()
        self.escapingFleet.startAllStateMachines()
        self.pursuingFleet.startAllStateMachines()

        self.shots = []
        self.shotsByTarget = {}

    def getHeightWidth(self):
        return (self.height, self.width)

    def getMaxLeftRightBottomTop(self):
        return (self.max_left,
                self.max_right,
                self.max_bottom,
                self.max_top)

    def start(self):
        pass

    def update(self,
               currentTime):
        if not self.current_time:
            self.current_time = currentTime
        timeElapsed = (currentTime - self.current_time)
        self.current_time = currentTime
        for canvasElement in self.getAllCanvasElements():
            if not canvasElement.active:
                continue
            canvasElement.update(timeElapsed=timeElapsed)

    def render(self):
        for element in self.getAllCanvasElements():
            element.draw()

    def getJumpPoint(self):
        return self.jumpPoint
    
    def getAllCanvasElements(self):
        return (self.escapingFleet.getAllShips() + 
                self.pursuingFleet.getAllShips() + 
                self.shots + 
                [self.jumpPoint])
        
    def getAllShips(self):
        return (self.escapingFleet.getAllShips() +
                self.pursuingFleet.getAllShips())
        
    def addShot(self,
                shot):
        self.shots.append(shot)
        target = shot.target
        shots_for_target = self.shotsByTarget.get(target)
        if shots_for_target is None:
            shots_for_target = self.shotsByTarget[target] = []
        shots_for_target.append(shot)
        
    def removeShot(self,
                   shot):
        self.shots.remove(shot)
        target = shot.target
        self.shotsByTarget[target].remove(shot)
        

verify.verifyClass(interfaces.IWorld, EscapeWorld)
