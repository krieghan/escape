import random
import agents, render, goalStates, statemachine, targetingsystem
from twodee.geometry import (calculate)

def getFleetReport(fleet):
    report = []
    for (clusterType, cluster) in fleet.flightGroups.items():
        for flightGroup in cluster:
            report.append('%s group' % clusterType)
            i = 0
            for ship in flightGroup.getAllShips():
                i += 1
                report.append('fighter %s: ' % i)
                report.append('\tcurrentState: %s' % ship.stateMachine.currentState.__name__)
                behaviors = []
                for actionName, action in ship.steeringController.actions.items():
                    if action is None:
                        continue
                    behaviors.append(actionName)
                report.append('\tsteeringbehaviors: %s' % behaviors)
    return '\n'.join(report)
                
            
class Fleet(object):
    def __init__(self,
                 fleetColor,
                 teamName):
        self.motherShip = None
        self.flightGroups = {'fighter' : [],
                             'bomber' : [],
                             'interceptor' : []}
        self.enemyFleet = None
        self.teamName = teamName
        self.fleetColor = fleetColor
        self.instancesOfFriendlyFire = 0
        
    def addFlightGroups(self,
                        flightGroups):
        for flightGroup in flightGroups:
            shipType = flightGroup.shipType
            self.flightGroups[shipType].append(flightGroup)
            for ship in flightGroup.ships:
                ship.startLife()
        
    def removeFlightGroup(self,
                          flightGroup):
        shipType = flightGroup.shipType
        self.flightGroups[shipType].remove(flightGroup)
        
    def setMotherShip(self,
                      motherShip):
        self.motherShip = motherShip
        
    def setEnemyFleet(self,
                      enemyFleet):
        self.enemyFleet = enemyFleet
        
    def getEnemyFleet(self):
        return self.enemyFleet
        
    def getFleetColor(self):
        return self.fleetColor
    
    def getAllFighters(self,
                       shipType=None):
        ships = []
        if shipType is not None:
            flightGroupClusters = [self.flightGroups[shipType]]
        else:
            flightGroupClusters = self.flightGroups.values()
        for cluster in flightGroupClusters:
            for flightGroup in cluster:
                ships.extend(flightGroup.getAllShips())
        return ships
            
    
    def getAllShips(self):
        ships = []
        ships.extend(self.getAllFighters())
        if self.motherShip:
            ships.append(self.motherShip)
        return ships
    
    def getAllEnemyShips(self):
        enemyFleet = self.enemyFleet
        return enemyFleet.getAllShips()
        
    def getMotherShip(self):
        return self.motherShip
    
    def startAllStateMachines(self):
        
        for ship in self.getAllShips():
            ship.startStateMachines()
        for flightGroupCluster in self.flightGroups.values():
            for flightGroup in flightGroupCluster:
                flightGroup.stateMachine.start()
            
class FlightGroup(object):
    def __init__(self,
                 fleet,
                 shipType,
                 startingState,
                 ships):
        self.fleet = fleet
        self.ships = []
        self.addShips(ships)
        self.shipType = shipType
        self.stateMachine = statemachine.StateMachine(owner=self,
                                                      currentState=startingState)
    
    def getAllShips(self):
        return self.ships
    
    def addShips(self,
                 ships):
        for ship in ships:
            ship.flightGroup = self
        self.ships.extend(ships)
        
    def removeShip(self,
                   ship):
        self.ships.remove(ship)
        if not self.ships:
            self.fleet.removeFlightGroup(self)
    
    def activateSteeringBehavior(self,
                                 behavior,
                                 *args):
        for ship in self.ships:
            ship.steeringController.activate(behavior,
                                             *args)
    
    def startStateMachine(self):
        self.stateMachine.start()
        for ship in self.ships:
            ship.startStateMachines()
    
    def setPosition(self,
                    position):
        for ship in self.ships:
            ship.setPosition(position)
            
    def setVelocity(self,
                    velocity):
        for ship in self.ships:
            ship.setVelocity(velocity)
    
    
            
def createFighterTurret(owner,
                        offset):
    rechargeTime = 15
    turret = agents.Turret(owner=owner,
                           rechargeTime=rechargeTime,
                           firingRange=10000,
                           offset=offset,
                           damage=5,
                           shotRenderer=render.drawLaserShot,
                           shotHeight=300,
                           shotSpeed=150,
                           shotWidth=None)
    return turret

def createLaserTurret(owner,
                      offset):
    rechargeTime = 25
    turret = agents.Turret(owner=owner,
                           rechargeTime=rechargeTime,
                           firingRange=10000,
                           offset=offset,
                           damage=10,
                           shotRenderer=render.drawLaserShot,
                           shotHeight=300,
                           shotSpeed=150,
                           shotWidth=None)
    return turret

def createLauncher(owner,
                   offset):
    rechargeTime = 300
    launcher = agents.Turret(owner=owner,
                             rechargeTime=rechargeTime,
                             firingRange=20000,
                             offset=offset,
                             damage=100,
                             shotRenderer=render.drawSpaceBomb,
                             shotHeight=300,
                             shotSpeed=50,
                             shotWidth=300)
    return launcher


def createBomber(fleet,
                 canvas,
                 carryOutMission,
                 globalState):
    length = 1000
    width = 500
    color = fleet.getFleetColor()
    bomber = agents.Ship(position=None,
                         length=length,
                         width=width,
                         velocity=(0, 1),
                         color=color,
                         canvas=canvas,
                         render=render.drawBomber,
                         mass=3,
                         maxSpeed=50,
                         maxForce=100,
                         health=100,
                         fleet=fleet,
                         mission=carryOutMission,
                         startingState=carryOutMission,
                         globalState=globalState)
    halfLength = length / 2.0
    turret = createLauncher(owner=bomber,
                            offset=(halfLength, 0))
    bomber.addTurrets([turret])
    return bomber

def createInterceptor(fleet,
                      canvas,
                      carryOutMission,
                      globalState):
    length = 1000
    width = 500
    color = fleet.getFleetColor()
    interceptor = agents.Ship(position=None,
                              length=length,
                              width=width,
                              velocity=(0, 1),
                              color=color,
                              canvas=canvas,
                              render=render.drawInterceptor,
                              mass=3,
                              maxSpeed=100,
                              maxForce=300,
                              health=100,
                              fleet=fleet,
                              startingState=carryOutMission,
                              mission=carryOutMission,
                              globalState=globalState)
    threeFifthsLength = (3.0 * length) / 5.0
    turret = createFighterTurret(owner=interceptor,
                                 offset=(threeFifthsLength, 0))
    interceptor.addTurrets([turret])
    return interceptor

def createFighter(fleet,
                  canvas,
                  carryOutMission,
                  globalState):
    length = 1000
    width = 500
    color = fleet.getFleetColor()
    fighter = agents.Ship(position=None,
                          length=length,
                          width=width,
                          velocity=(0, 1),
                          color=color,
                          canvas=canvas,
                          render=render.drawFighter,
                          mass=3,
                          maxSpeed=100,
                          maxForce=300,
                          health=100,
                          fleet=fleet,
                          startingState=carryOutMission,
                          mission=carryOutMission,
                          globalState=globalState)
    halfLength = length / 2.0
    turret = createFighterTurret(owner=fighter,
                                 offset=(halfLength, 0))
    fighter.addTurrets([turret])
    return fighter

def createInterceptorFlightGroup(fleet,
                                 canvas):
    globalState = goalStates.FighterGlobalState
    carryOutMission = goalStates.DestroyGreatestThreatToMothership
    interceptor1 = createInterceptor(fleet=fleet,
                                     canvas=canvas,
                                     carryOutMission=carryOutMission,
                                     globalState=globalState)
    interceptor2 = createInterceptor(fleet=fleet,
                                     canvas=canvas,
                                     carryOutMission=carryOutMission,
                                     globalState=globalState)
    interceptor3 = createInterceptor(fleet=fleet,
                                     canvas=canvas,
                                     carryOutMission=carryOutMission,
                                     globalState=globalState)
    interceptor4 = createInterceptor(fleet=fleet,
                                     canvas=canvas,
                                     carryOutMission=carryOutMission,
                                     globalState=globalState)
    interceptorGroup = FlightGroup(fleet=fleet,
                                   shipType='interceptor',
                                   startingState=goalStates.FlightGroupState,
                                   ships=(interceptor1,
                                          interceptor2,
                                          interceptor3,
                                          interceptor4))
    interceptorGroup.activateSteeringBehavior('flock',
                                              interceptorGroup.getAllShips())
    return interceptorGroup

def createBomberFlightGroup(fleet,
                            canvas):
    carryOutMission = goalStates.DestroyClosestEnemyCapitalShip
    globalState = goalStates.FighterGlobalState
    bomber1 = createBomber(fleet=fleet,
                           canvas=canvas,
                           carryOutMission=carryOutMission,
                           globalState=globalState)
    bomber2 = createBomber(fleet=fleet,
                           canvas=canvas,
                           carryOutMission=carryOutMission,
                           globalState=globalState)
    bomber3 = createBomber(fleet=fleet,
                           canvas=canvas,
                           carryOutMission=carryOutMission,
                           globalState=globalState)
    bomber4 = createBomber(fleet=fleet,
                           canvas=canvas,
                           carryOutMission=carryOutMission,
                           globalState=globalState)
    bomberGroup = FlightGroup(fleet=fleet,
                              shipType='bomber',
                              startingState=goalStates.FlightGroupState,
                              ships=(bomber1,
                                     bomber2,
                                     bomber3,
                                     bomber4))
    bomberGroup.activateSteeringBehavior('flock',
                                         bomberGroup.getAllShips())
    return bomberGroup
    

def createFighterFlightGroup(fleet,
                             canvas):
    carryOutMission = goalgoalStates.DestroyClosestEnemyFighter
    globalState = goalStates.FighterGlobalState
    fighter1 = createFighter(fleet=fleet,
                             canvas=canvas,
                             carryOutMission=carryOutMission,
                             globalState=globalState)
    fighter2 = createFighter(fleet=fleet,
                             canvas=canvas,
                             carryOutMission=carryOutMission,
                             globalState=globalState)
    fighter3 = createFighter(fleet=fleet,
                             canvas=canvas,
                             carryOutMission=carryOutMission,
                             globalState=globalState)
    fighter4 = createFighter(fleet=fleet,
                             canvas=canvas,
                             carryOutMission=carryOutMission,
                             globalState=globalState)
    fighterGroup = FlightGroup(fleet=fleet,
                               shipType='fighter',
                               startingState=goalStates.FlightGroupState,
                               ships=(fighter1, 
                                      fighter2, 
                                      fighter3, 
                                      fighter4))
    fighterGroup.activateSteeringBehavior('flock',
                                          fighterGroup.getAllShips())
    
    return fighterGroup

def createMotherShip(fleet,
                     canvas,
                     position,
                     carryOutMission):
    color = fleet.getFleetColor()
    length = 2000
    width = 6000
    motherShip =\
        agents.Ship(position=position,
                    length=length,
                    width=width,
                    velocity=(0, 1),
                    color=color,
                    canvas=canvas,
                    render=render.drawMotherShip,
                    mass=50,
                    maxSpeed=5,
                    maxForce=20,
                    health=10000,
                    fleet=fleet,
                    mission=carryOutMission,
                    startingState=carryOutMission)
    halfWidth = width / 2.0
    halfLength = length / 2.0
    sixthWidth = width / 6.0
    turret1 = createLaserTurret(owner=motherShip,
                                offset=(0, halfWidth))
    turret2 = createLaserTurret(owner=motherShip,
                                offset=(-halfLength, sixthWidth))
    turret3 = createLaserTurret(owner=motherShip,
                                offset=(-halfLength, -sixthWidth))
    turret4 = createLaserTurret(owner=motherShip,
                                offset=(0, -halfWidth))
    turret5 = createLaserTurret(owner=motherShip,
                                offset=(halfLength, -sixthWidth))
    turret6 = createLaserTurret(owner=motherShip,
                                offset=(halfLength, sixthWidth))
    
    motherShip.addTurrets([turret1,
                           turret2,
                           turret3,
                           turret4,
                           turret5,
                           turret6])
    return motherShip

def addFlightGroupsToHangar(howMany,
                            factory,
                            fleet,
                            canvas,
                            motherShip):
    groups = []
    for i in range(howMany):
        flightGroup = factory(fleet=fleet,
                              canvas=canvas)
        groups.append(flightGroup)
        
    motherShip.addFlightGroupsToHangar(groups)

def createEscapingFleet(canvas):
    fleetColor = (0, 0, 1)
    escapingFleet = Fleet(fleetColor=fleetColor,
                          teamName='defender')
    escapingMotherShip = createMotherShip(escapingFleet,
                                          canvas,
                                          position=(30000, 30000),
                                          carryOutMission=goalStates.EscapeToJumpPoint)
    
    addFlightGroupsToHangar(howMany=20,
                            factory=createBomberFlightGroup,
                            fleet=escapingFleet,
                            canvas=canvas,
                            motherShip=escapingMotherShip)
    addFlightGroupsToHangar(howMany=20,
                            factory=createInterceptorFlightGroup,
                            fleet=escapingFleet,
                            canvas=canvas,
                            motherShip=escapingMotherShip)
    
    escapingFleet.setMotherShip(escapingMotherShip)
    return escapingFleet

def createPursuingFleet(canvas):
    fleetColor = (1, 0, 0)
    pursuingFleet = Fleet(fleetColor=fleetColor,
                          teamName='attacker')
    pursuingMotherShip = createMotherShip(pursuingFleet,
                                          canvas,
                                          position=(12000, 12000),
                                          carryOutMission=goalStates.AttackEscapingMothership)
    addFlightGroupsToHangar(howMany=20,
                            factory=createBomberFlightGroup,
                            fleet=pursuingFleet,
                            canvas=canvas,
                            motherShip=pursuingMotherShip)
    addFlightGroupsToHangar(howMany=20,
                            factory=createInterceptorFlightGroup,
                            fleet=pursuingFleet,
                            canvas=canvas,
                            motherShip=pursuingMotherShip)
    pursuingFleet.setMotherShip(pursuingMotherShip)
    return pursuingFleet