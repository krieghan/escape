import math, random
from zope.interface import implements, verify

from game_common import interfaces, statemachine
from game_common.twodee.geometry import (
                         calculate,
                         vector,
                         convert)
from game_common.twodee.steering import steeringcontroller
from escape import render

class Ship(object):
    
    implements(interfaces.Steerable)
    
    def __init__(self,
                 position,
                 length,
                 width,
                 velocity,
                 color,
                 render,
                 world,
                 mass,
                 maxSpeed,
                 maxForce,
                 fleet,
                 health,
                 flightGroup=None,
                 launchOffset=None,
                 startingState=None,
                 mission=None,
                 globalState=None,
                 targetingSystem=None,
                 name=None):
        self.name = name
        self.length = length
        self.width = width
        self.lengthSquared = length * length
        self.widthSquared = width * width
        self.position = position
        self.velocity = velocity
        self.color = color
        self.normalColor = color
        self.timeOfNormalColor = None
        self.timeOfNextLaunch = None
        self.msBetweenLaunches = 3000
        self.msOfShotColor = 200
        self.maxSpeed = maxSpeed
        self.throttleSpeed = maxSpeed
        self.maxForce = maxForce
        self.world = world
        self.targetingSystem = targetingSystem
        self.steeringController = steeringcontroller.SteeringController(agent=self)
        self.mission = mission
        self.steeringStateMachine = statemachine.StateMachine(owner=self,
                                                              currentState=None,
                                                              globalState=None,
                                                              name='steering')
        self.goalStateMachine = statemachine.StateMachine(owner=self,
                                                          currentState=startingState,
                                                          globalState=globalState,
                                                          name='goal')
        self.stateMachines = [self.goalStateMachine, self.steeringStateMachine]
        self.flightGroup = flightGroup
        self.target = None
        self.render = render
        self.turrets = []
        self.flightGroups = {'fighter' : [],
                             'bomber' : [],
                             'interceptor' : []}
        self.targettingTurrets = []
        self.attackers = []
        self.active = True
        
        
        self.fleet = fleet
        self.mass = mass
        self.minDetectionLength = 120
        halfWidth = width / 2.0
        halfLength = length / 2.0
        
        self.hangarEntryThresholdSquared = 1000000
        
        self.boundingBox = (halfLength, halfWidth, -halfLength, -halfWidth)
        speed = vector.getMagnitude(velocity)
        self.obstacleDetectionDimensions =\
            [self.minDetectionLength + (speed / maxSpeed) * self.minDetectionLength,
             width]
        if launchOffset is None:
            launchOffset = (-halfWidth - 200, 0)
        self.launchOffset = launchOffset
        self.health = health
        self.totalHealth = health
        
        '''
        debugObserver = world.frame.childFrames.get('%sDebug' % fleet.teamName)
        self.observers = [debugObserver]
        '''
        self.observers = []
        
        
    def getActive(self):
        return self.active
    
    def draw(self):
        self.render(self)
    
    
    #observable
    def startLife(self):
        for observer in self.observers:
            observer.notifyShipStartLife(self)
    
    def endLife(self):
        self.active = False
        while self.targettingTurrets:
            targettingTurret = self.targettingTurrets[0]
            targettingTurret.notifyOfDeath(self)
            
        
        if self.flightGroup:
            self.flightGroup.removeShip(self)
        elif self.fleet.motherShip == self:
            self.fleet.motherShip = None
            
        for observer in self.observers:
            observer.notifyShipEndLife(self)
    
    
    def addFlightGroupsToHangar(self,
                                flightGroups):
        for flightGroup in flightGroups:
            shipType = flightGroup.shipType
            self.flightGroups[shipType].append(flightGroup)
            
    def removeFlightGroup(self,
                          flightGroup):
        groupType = flightGroup.shipType
        self.flightGroups[groupType].remove(flightGroup)
        
    def pickup(self,
               ship):
       ship.endLife() 
        
    
    def acquireTarget(self):
        self.setTarget(self.targetingSystem.acquireTarget(self))
        return self.target
    
    def launch(self):
        current_time = self.world.current_time
        if not self.flightGroups:
            return
        
        if current_time < self.timeOfNextLaunch:
            return
        else:
            self.timeOfNextLaunch = current_time + self.msBetweenLaunches
        
        desiredNumberOfFriendlyBombers = 1
        desiredNumberOfFriendlyFighters = 1
        
        fleet = self.fleet
        enemyFleet = fleet.getEnemyFleet()
        friendlyFlightGroups = fleet.flightGroups
        enemyFlightGroups = enemyFleet.flightGroups
        onboardFlightGroups = self.flightGroups
        
        onboardInterceptorGroups = onboardFlightGroups['interceptor']
        onboardBomberGroups = onboardFlightGroups['bomber']
        onboardFighterGroups = onboardFlightGroups['fighter']
        friendlyInterceptorGroups = friendlyFlightGroups['interceptor']
        friendlyBomberGroups = friendlyFlightGroups['bomber']
        friendlyFighterGroups = friendlyFlightGroups['fighter']
        enemyBomberGroups = enemyFlightGroups['bomber']
        
        if (len(enemyBomberGroups) > len(friendlyInterceptorGroups) and
            len(onboardInterceptorGroups) > 0):
            groupToLaunch = onboardInterceptorGroups[0]
        elif (len(friendlyBomberGroups) < desiredNumberOfFriendlyBombers and
              len(onboardBomberGroups) > 0):
            groupToLaunch = onboardBomberGroups[0]
        elif (len(friendlyFighterGroups) < desiredNumberOfFriendlyFighters and
              len(onboardFighterGroups) > 0):
            groupToLaunch = onboardFighterGroups[0]
        else:
            return
        
        carrierPosition = self.getPosition()
        worldLaunchOffset = convert.vectorToWorldSpace(self.launchOffset,
                                                       carrierPosition,
                                                       self.getDirection())
        newPosition = calculate.addPointAndVector(carrierPosition,
                                                  worldLaunchOffset)
        groupToLaunch.setPosition(newPosition)
        groupToLaunch.setVelocity((1, 0))
        self.removeFlightGroup(groupToLaunch)
        fleet.addFlightGroups([groupToLaunch])
        groupToLaunch.startStateMachine()
        
    def engageThrottle(self,
                       speed):
        self.throttleSpeed = min(speed, self.maxSpeed)
        
    def disengageThrottle(self):
        self.throttleSpeed = self.maxSpeed
        
    
    def update(self,
               timeElapsed):
        current_time = self.world.current_time
        if self.timeOfNormalColor and current_time < self.timeOfNormalColor:
            self.color = (random.random(), random.random(), random.random())
        elif self.timeOfNormalColor:
            self.timeOfNormalColor = None
            self.color = self.normalColor

        world = self.world
        maxspeed = self.maxSpeed
        throttlespeed = self.throttleSpeed
        maxforce = self.maxForce
        minDetectionLength = self.minDetectionLength
        for stateMachine in self.stateMachines:
            stateMachine.update()
        for turret in self.turrets:
            turret.update(timeElapsed)
            
        self.launch()
        
        force = self.steeringController.calculate()
        force = vector.truncate(vectorTuple=force,
                                cap=maxforce)
        
        acceleration = calculate.multiplyVectorAndScalar(vector=force,
                                                         scalar=timeElapsed / (self.mass * 1000.0))
        
        velocity = calculate.addVectors(self.velocity,
                                        acceleration)

        velocity = vector.truncate(velocity,
                                   throttlespeed)
        self.velocity = velocity                

        speed = vector.getMagnitude(velocity)
       
        (x, y) = calculate.addPointAndVector(self.position,
                                             velocity)
        self.position = (x, y)
                
        self.obstacleDetectionDimensions[0] =\
            minDetectionLength + (speed / maxspeed) * minDetectionLength 
    
    def setPosition(self,
                    position):
        self.position = position
        
    def setVelocity(self,
                    velocity):
        self.velocity = velocity
    
    def getMaxForce(self):
        return self.maxForce
    
    def getMaxSpeed(self):
        return self.maxSpeed
    
    def getVelocity(self):
        return self.velocity
    
    def getHeading(self):
        return vector.normalize(self.velocity)
    
    def getLength(self):
        return self.length
    
    def getWidth(self):
        return self.width
    
    def getSpeed(self):
        return vector.getMagnitude(self.velocity)
    
    def getSteeringController(self):
        return self.steeringController
    
    def setTargetingSystem(self, targetingSystem):
        self.targetingSystem = targetingSystem
        

    def getDirectionDegrees(self):
        return vector.getDirectionDegrees(self.velocity)
    
    def getDirection(self):
        return vector.getDirectionRadians(self.velocity)

    def getObstacleDetectionDimensions(self):
        return self.obstacleDetectionDimensions
    
    def getPosition(self):
        return self.position
    
    def getTarget(self):
        return self.target
    
    def getMaximumFiringRange(self):
        return max([turret.firingRange
                    for turret in self.turrets])
        
    def getMaximumFiringRangeSquared(self):
        return max([turret.firingRangeSquared
                    for turret in self.turrets])
    
    def startStateMachines(self):
        for stateMachine in self.stateMachines:
            stateMachine.start()
    
    def addTurrets(self,
                   turrets):
        self.turrets.extend(turrets)
    
    def setTarget(self,
                  newTarget):
        if self.target:
            self.target.removeFromAttackers(self)
        self.target = newTarget
        if newTarget is not None:
            newTarget.addToAttackers(self)
    
    def notifyOfDeath(self,
                      agent):
        self.setTarget(None)

    def addToAttackers(self,
                       attacker):
        self.attackers.append(attacker)
        
    def removeFromAttackers(self,
                            attacker):
        self.attackers.remove(attacker)
    
    def addToTargettingTurrets(self,
                               targeter):
        self.targettingTurrets.append(targeter)
        
    def removeFromTargettingTurrets(self,
                            targeter):
        self.targettingTurrets.remove(targeter)

    def hitBy(self,
              shot):
        current_time = self.world.current_time
        fleet = self.fleet
        enemyFleet = fleet.getEnemyFleet()
        if shot.fromTurret.owner.fleet == fleet:
            fleet.instancesOfFriendlyFire += 1
        self.timeOfNormalColor = current_time + self.msOfShotColor
        self.health -= shot.damage
        
        for observer in self.observers:
            observer.notifyShipHit(self)
        
        if self.health <= 0:
            self.endLife()
        
    def intersectsPoint(self,
                        point):
        shipPosition = self.getPosition()
        shipToPoint = calculate.subtractPoints(point,
                                               shipPosition)
        distanceSquaredToPoint = vector.getMagnitudeSquared(shipToPoint)
        if (distanceSquaredToPoint > self.lengthSquared or
            distanceSquaredToPoint > self.widthSquared):
            return None
        
        directionRadians = self.getDirection()
        localPoint = convert.pointToLocalSpace(point,
                                               shipPosition,
                                               directionRadians)
        (topy, rightx, bottomy, leftx) = self.boundingBox
        x, y = localPoint
        if (x > leftx and
            x < rightx and
            y < topy and
            y > bottomy):
            return True

verify.verifyClass(interfaces.Steerable, Ship)
    
    
class Turret(object):
    
    implements(interfaces.Renderable)
    
    def __init__(self,
                 owner,
                 rechargeTime,
                 firingRange,
                 offset,
                 damage,
                 shotRenderer,
                 shotHeight,
                 shotWidth,
                 shotSpeed):
        self.owner = owner
        self.rechargeTime = rechargeTime
        self.offset = offset
        self.target = None
        self.timeRecharged = None
        self.firingRange = firingRange
        self.firingRangeSquared = firingRange * firingRange
        self.position = None
        self.damage = damage
        self.shotRenderer = shotRenderer
        self.shotHeight = shotHeight
        self.shotWidth = shotWidth
        self.shotSpeed = shotSpeed
        self.obstructed = False
        self.clearShotTolerance = .15
        self.active = True
        
    def getLength(self):
        return 0
    
    def getWidth(self):
        return 0

    def draw(self):
        pass

    def getActive(self):
        pass
        
    def updatePosition(self):
        owner = self.owner
        ownerPosition = owner.getPosition()
        position = convert.pointToWorldSpace(self.offset,
                                             ownerPosition,
                                             owner.getDirection())
        ownerToGun = calculate.subtractPoints(position,
                                              ownerPosition)
        self.heading = vector.normalize(ownerToGun)
        self.position = position
        
    
    def getPosition(self):
        return self.position
    
    def getTarget(self):
        return self.target

    
    def setTarget(self,
                  newTarget):
        if self.target:
            self.target.removeFromTargettingTurrets(self)
        self.target = newTarget
        if newTarget is not None:
            newTarget.addToTargettingTurrets(self)
    
    def notifyOfDeath(self,
                      agent):
        self.setTarget(None)

    def acquireTemporaryTarget(self):
        '''Collect any targets that are in range.  Then, collect from those
           the targets to which we have a clear shot.  Find the one that is closest.
           That is the temporary target.'''
        turretPosition = self.getPosition()
        owner = self.owner
        fleet = owner.fleet
        
        enemiesInRange = []
        for enemyShip in fleet.getAllEnemyShips():
            if not self.targetIsInRange(enemyShip):
                continue
            if not self.haveClearShotOfTarget(enemyShip):
                continue
            
            enemiesInRange.append(enemyShip)
                
        closestShip = None
        closestDistanceSquared = None
        
        for enemyShip in enemiesInRange:
            enemyPosition = enemyShip.getPosition()
            turretToEnemy = calculate.subtractPoints(enemyPosition,
                                                     turretPosition)
            distanceSquaredToEnemy = vector.getMagnitudeSquared(turretToEnemy)
            if closestShip is None or distanceSquaredToEnemy < closestDistanceSquared:
                closestShip = enemyShip
                closestDistanceSquared = distanceSquaredToEnemy
        
        if closestShip:
            self.setTarget(closestShip)
            return closestShip
        else:
            return None
    
    def handleTargettingAndFiring(self):
        '''If our gun is not ready to fire, return immediately and do not bother targetting or firing.
           If the agent's target is obstructed, mark the gun as obstructed so that we may find a clear shot.
           If the agent's target is in range and unobstructed, acquire it.
           If the agent's target is either out of range or obstructed, we need to find a temporary target.
           With regards to a temporary target, If:
               We do not have one
               It is out of range
               It is obstructed
           Then we need to acquire a new one that is in range and unobstructed.
           If our acquisition fails, simply do not fire.  Set the target to None.
           If we find a good temporary target, fire on it.'''
            
        if not self.readyToFire():
            return
        
        self.obstructed = False
        
        gunTarget = self.getTarget()
        ownerTarget = self.owner.getTarget()
        
        ownerTargetEligible = True
        if ownerTarget is None:
            ownerTargetEligible = False
        else:
            haveClearShotOfOwnerTarget = self.haveClearShotOfTarget(ownerTarget)
            if not haveClearShotOfOwnerTarget:
                self.obstructed = True
        
            if (self.targetIsInRange(ownerTarget) and
                haveClearShotOfOwnerTarget):
                if gunTarget != ownerTarget:
                    self.setTarget(ownerTarget)
            else:
                ownerTargetEligible = False

        if ownerTargetEligible:
            temporaryTargetEligible = False
        else:
            if (gunTarget is None or
                not self.targetIsInRange(gunTarget) or
                not self.haveClearShotOfTarget(gunTarget)):
                target = self.acquireTemporaryTarget()
                if target:
                    temporaryTargetEligible = True
                else:
                    temporaryTargetEligible = False
                
            else:
                temporaryTargetEligible = True
                
        gunTarget = self.getTarget()
        if gunTarget and (ownerTargetEligible or temporaryTargetEligible):
            self.fire(gunTarget)
            
        
    def update(self, timeElapsed):
        self.obstructed = False
        self.updatePosition()
        self.handleTargettingAndFiring()
         
    def haveClearShotOfTarget(self,
                              target):
        owner = self.owner
        fleet = owner.fleet
        turretPosition = self.getPosition()
        targetPosition = target.getPosition()
        turretToTarget = calculate.subtractPoints(targetPosition,
                                                  turretPosition)
        distanceSquaredToTarget = vector.getMagnitudeSquared(turretToTarget)
        headingToTarget = vector.normalize(turretToTarget)
        for friendlyShip in fleet.getAllShips():
            friendPosition = friendlyShip.getPosition()
            turretToFriend = calculate.subtractPoints(friendPosition,
                                                      turretPosition)
            distanceSquaredToFriend = vector.getMagnitudeSquared(turretToFriend)
            if distanceSquaredToFriend > distanceSquaredToTarget:
                continue
            
            headingToFriend = vector.normalize(turretToFriend)
            dotProductOfFriendAndTarget = calculate.dotProduct(headingToTarget,
                                                               headingToFriend)
            if calculate.withinTolerance(dotProductOfFriendAndTarget,
                                         1,
                                         self.clearShotTolerance):
                return False
        
        return True
    
    def targetIsInRange(self,
                        target):
        gunPosition = self.getPosition()
        targetPosition = target.getPosition()
        gunToTarget = calculate.subtractPoints(targetPosition,
                                               gunPosition)
        distanceSquaredToTarget = vector.getMagnitudeSquared(gunToTarget)
        headingToTarget = vector.normalize(gunToTarget)
        headingDotProduct = calculate.dotProduct(self.heading,
                                                 headingToTarget) 
        if (distanceSquaredToTarget < self.firingRangeSquared and
            headingDotProduct > 0):
            return True
        
        return False
    
    def readyToFire(self):
        owner = self.owner
        world = owner.world
        if self.timeRecharged is None or world.current_time >= self.timeRecharged:
            return True
        
        return False
    
    def predictFuturePosition(self,
                              source,
                              target,
                              shotSpeed):
        sourcePosition = source.getPosition()
        targetPosition = target.getPosition()
        targetVelocity = target.getVelocity()
        targetSpeed = target.getSpeed()
        sourceToTarget = calculate.subtractPoints(targetPosition,
                                                  sourcePosition)
        manhattanDistanceToTarget = vector.getManhattanMagnitude(sourceToTarget)
        lookAheadTime = manhattanDistanceToTarget / (shotSpeed + targetSpeed)
    
        lookAheadVector = calculate.multiplyVectorAndScalar(targetVelocity,
                                                            lookAheadTime)
    
        lookAheadPosition = calculate.addPointAndVector(targetPosition,
                                                        lookAheadVector)
        return lookAheadPosition
    
    def fire(self,
             target):
        owner = self.owner
        world = owner.world
        position = self.getPosition()
        speed = owner.getSpeed()
        shotSpeed = speed + self.shotSpeed
        
        predictedPosition = self.predictFuturePosition(source=self,
                                                       target=target,
                                                       shotSpeed=shotSpeed)
                                                       
        shotToPredictedPosition = calculate.subtractPoints(predictedPosition,
                                                           position)
        shotVelocity = vector.setMagnitude(shotToPredictedPosition,
                                           shotSpeed)
        shot = Shot(fromTurret=self,
                    velocity=shotVelocity,
                    position=position,
                    maxDistance=self.firingRange,
                    render=self.shotRenderer,
                    height=self.shotHeight,
                    width=self.shotWidth,
                    color=(1, 1, 1),
                    world=world,
                    damage=self.damage,
                    target=target)
        world.addShot(shot)
        self.timeRecharged = world.current_time + self.rechargeTime

verify.verifyClass(interfaces.Renderable, Turret)

class Shot(object):
    
    implements(interfaces.Steerable)
    
    def __init__(self,
                 fromTurret,
                 velocity,
                 position,
                 maxDistance,
                 height,
                 width,
                 color,
                 render,
                 world,
                 damage,
                 target):
        self.velocity = velocity
        self.startingPosition = position
        self.position = position
        self.maxDistanceSquared = maxDistance * maxDistance
        self.render = render
        self.height = height
        self.width = width
        self.color = color
        self.world = world
        self.fromTurret = fromTurret
        self.damage = damage
        self.target = target
        self.active = True
    
    
    def getActive(self):
        return self.active

    def hit(self):
        world = self.world
        owner = self.fromTurret.owner
        shotPosition = self.position
        for ship in world.getAllShips():
            if owner == ship:
                continue
            if ship.intersectsPoint(shotPosition):
                return ship
            
        return None
    
    def update(self,
               timeElapsed):
        world = self.world
        currentPosition = self.position
        shipHit = self.hit()
        if shipHit:
            shipHit.hitBy(self)
            world.removeShot(self)
            self.active = False
            return
        
        
        
        originToCurrent = calculate.subtractPoints(currentPosition,
                                                   self.startingPosition)
        distanceSquaredFromOrigin = vector.getMagnitudeSquared(originToCurrent)
        
        
        
        if distanceSquaredFromOrigin > self.maxDistanceSquared:
            world.removeShot(self)
            return
        
        (x, y) = calculate.addPointAndVector(currentPosition,
                                             self.velocity)
        self.position = (x,
                         y)
    
    def draw(self):
        self.render(self)
        
    def getPosition(self):
        return self.position
    
    def getDirectionDegrees(self):
        return vector.getDirectionDegrees(self.velocity)
    
    def getDirection(self):
        return vector.getDirection(self.velocity)

    def getSpeed(self):
        return vector.getMagnitude(self.velocity)
    
    def getVelocity(self):
        return self.velocity
    
    def getLength(self):
        return self.height
    
    def getWidth(self):
        return self.width
    
    def getHeading(self):
        return vector.normalize(self.velocity)
    
    
verify.verifyClass(interfaces.Moveable, Shot)

class Stationary(object):
    
    implements(interfaces.Renderable)
    
    def __init__(self,
                 position,
                 length,
                 width,
                 render,
                 color):
        self.position = position
        self.length = length
        self.width = width
        self.render = render
        self.color = color
        self.active = True
        
    def getActive(self):
        return self.active

    def draw(self):
        self.render(self)
        
    def getPosition(self):
        return self.position

    def update(self,
               timeElapsed):
        pass
    
    def getLength(self):
        return length
    
    def getWidth(self):
        return width
    
verify.verifyClass(interfaces.Renderable, Stationary)
    
