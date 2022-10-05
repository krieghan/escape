import zope.interface
from zope.interface import verify

from game_common import statemachine
from game_common.twodee.geometry import (
                             calculate,
                             convert,
                             vector)
        
#Dive & Break (for fighters)
        
breakThresholdSquared = 10000 ** 2
diveThresholdSquared = 1000 ** 2

def plotLocalRouteAroundTarget(owner,
                               target):
    steeringController = owner.steeringController
    ownerPosition = owner.getPosition()
    targetPosition = target.getPosition()
    ownerToTarget = calculate.subtractPoints(targetPosition,
                                             ownerPosition)
    distanceToTarget = vector.getMagnitude(ownerToTarget)
    optimalPathDistance = min(distanceToTarget,
                              owner.getMaximumFiringRange())
    
    #These are the eight "compass" directions, projected
    #in the target's local space
    vectors = ((0, 1),
               (1, 1),
               (1, 0),
               (-1, 1),
               (-1, 0),
               (-1, -1),
               (0, -1),
               (1, -1))
    
    #Now scale the directions so that they have my magnitude.
    #We can treat these vectors as points in an octagonal
    #path around the target - a path scaled to an optimal distance.
    pathPoints = [calculate.multiplyVectorAndScalar(normalizedVector,
                                                    optimalPathDistance)
                  for normalizedVector in vectors]
    
    #Find the point in the path that is closest to my position.
    
    ownerLocalPosition = convert.pointToLocalSpace(ownerPosition,
                                                   targetPosition,
                                                   target.getDirection())
    
    closestDistanceSquared = None
    closestIndex = None
    for index in range(len(pathPoints)):
        pathPoint = pathPoints[index]
        ownerToPathPoint = calculate.subtractPoints(pathPoint,
                                                    ownerLocalPosition)
        distanceSquaredToPathPoint =\
            vector.getMagnitudeSquared(ownerToPathPoint)
        if (closestDistanceSquared is None or 
            distanceSquaredToPathPoint < closestDistanceSquared):
            closestIndex = index
            closestDistanceSquared = distanceSquaredToPathPoint
            
    
    #Now "shift" the path so that my closest point is the first in the list.
    
    path = pathPoints[closestIndex:] + pathPoints[:closestIndex]
        
    
    #Plot a course to visit the path.  If at any point I find a clear shot to the target,
    #I will dive at it.
    
    steeringController.plotPath(path,
                                closed=True)


@zope.interface.implementer(statemachine.IState)
class FindClearShot(object):
    
    stateCluster = 'Attack'
    
    @classmethod 
    def enter(cls,
              owner):
        target = owner.getTarget()
        plotLocalRouteAroundTarget(owner,
                                   target)
        steeringController = owner.steeringController
        steeringController.activate('followpath',
                                    target)
    
    @classmethod
    def execute(cls,
                owner):
        #If I have a clear path to the target (whether it is a major approach vector or not)
        #I will use it to dive in on the target.
        if not areAnyGunsObstructed(owner):
            owner.steeringStateMachine.changeState(Dive)
    
    @classmethod
    def exit(cls,
             owner):
        steeringController = owner.steeringController
        steeringController.deactivate('followpath')
        
verify.verifyClass(statemachine.IState, FindClearShot)


def areAnyGunsObstructed(owner):
    turrets = owner.turrets
    anyGunsObstructed = any([turret.obstructed for turret in turrets])
    return anyGunsObstructed

def pastDiveThreshold(owner,
                      target):
    targetPosition = target.getPosition()
    ownerPosition = owner.getPosition()
    ownerToTarget = calculate.subtractPoints(targetPosition,
                                                 ownerPosition)
    distanceSquaredToTarget = vector.getMagnitudeSquared(ownerToTarget)
    if distanceSquaredToTarget < diveThresholdSquared:
        return True
    else:
        return False
    
def pastBreakThreshold(owner,
                       target):
    targetPosition = target.getPosition()
    ownerPosition = owner.getPosition()
    ownerToTarget = calculate.subtractPoints(targetPosition,
                                             ownerPosition)
    distanceSquaredToTarget = vector.getMagnitudeSquared(ownerToTarget)
    if distanceSquaredToTarget > breakThresholdSquared:
        return True
    else:
        return False

def acquireTargetOrEscort(owner):
    target = owner.getTarget()
    if not target:
        target = owner.acquireTarget()
        if not target:
            owner.goalStateMachine.changeState(EscortMotherShip)
            return None
    return target

def withinFiringRange(owner,
                      target):
    ownerPosition = owner.getPosition()
    targetPosition = target.getPosition()
    ownerToTarget = calculate.subtractPoints(targetPosition,
                                             ownerPosition)
    distanceSquaredToTarget = vector.getMagnitudeSquared(ownerToTarget)
    if distanceSquaredToTarget < owner.getMaximumFiringRangeSquared():
        return True
    else:
        return False
        

@zope.interface.implementer(statemachine.IState)
class Cruise(object):
    
    @classmethod
    def getTarget(cls,
                  owner):
        target = acquireTargetOrEscort(owner)
        return target
    
    @classmethod
    def enter(cls,
              owner):
        target = cls.getTarget(owner)
        owner.steeringController.activate('pursue',
                                          target)
    
    @classmethod
    def execute(cls,
                owner):
        target = cls.getTarget(owner)
        if target is None:
            return
        
        stateMachine = owner.stateMachine
        if areAnyGunsObstructed(owner):
            stateMachine.changeState(FindClearShot)
            return
        if pastDiveThreshold(owner,
                             target):
            stateMachine.changeState(Break)
            return
        if not withinFiringRange(owner,
                                 target):
            stateMachine.changeState(Dive)
            return
        
        targetSpeed = target.getSpeed()
        owner.engageThrottle(targetSpeed)
        
    
    @classmethod
    def exit(cls,
             owner):
        owner.disengageThrottle()
        owner.steeringController.deactivate('pursue')

verify.verifyClass(statemachine.IState, Cruise)


@zope.interface.implementer(statemachine.IState)
class Dive(object):
    stateCluster = 'Attack'
    
    @classmethod
    def pursueTarget(cls,
                     owner):
        target = owner.getTarget()
        if not target:
            raise Exception()
        steeringController = owner.steeringController
        steeringController.activate('pursue',
                                    target)
    
    @classmethod
    def acquireTarget(cls,
                      owner):
        target = owner.acquireTarget()
        if target:
            cls.pursueTarget(owner)
        else:
            return None
    
    @classmethod
    def enter(cls,
              owner):
        if owner.getTarget():
            cls.pursueTarget(owner)
        else:
            cls.acquireTarget(owner)
        
    @classmethod
    def execute(cls,
                owner):
        steeringStateMachine = owner.steeringStateMachine
        target = owner.getTarget() or cls.acquireTarget(owner)
        if target is None:
            return
        
        if areAnyGunsObstructed(owner):
            steeringStateMachine.changeState(FindClearShot)
        elif pastDiveThreshold(owner,
                               target):
            steeringStateMachine.changeState(Break)
            
        
    @classmethod
    def exit(cls,
             owner):
        steeringController = owner.steeringController
        steeringController.deactivate('pursue')
        
verify.verifyClass(statemachine.IState, Dive)

    
@zope.interface.implementer(statemachine.IState)
class Break(object):
    
    stateCluster = 'Attack'
    
    @classmethod
    def acquireTarget(cls,
                      owner):
        target = owner.acquireTarget()
        if target:
            steeringController = owner.steeringController
            steeringController.activate('evade',
                                        target)
        else:
            return None
    
    @classmethod
    def enter(cls,
              owner):
        if not owner.getTarget():
            cls.acquireTarget(owner)
    
    @classmethod
    def execute(cls,
                owner):
        from escape import goalStates
        steeringStateMachine = owner.steeringStateMachine
        target = owner.getTarget() or cls.acquireTarget(owner)
        if target is None:
            steeringStateMachine.changeState(goalStates.EscortMotherShip)
            return
        
        if pastBreakThreshold(owner,
                              target):
            steeringStateMachine.changeState(Dive)
        
    
    @classmethod
    def exit(cls,
             owner):
        steeringController = owner.steeringController
        steeringController.deactivate('evade')

verify.verifyClass(statemachine.IState, Break)


