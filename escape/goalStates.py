from zope.interface import implementer, verify

from game_common import statemachine
from escape import targetingsystem, steeringStates

from game_common.twodee.geometry import (
                             calculate,
                             convert,
                             vector)

#Defenders

@implementer(statemachine.IState)
class EscapeToJumpPoint(object):
    @classmethod
    def enter(cls,
              owner):
        steeringController = owner.getSteeringController()
        world = owner.world
        jumpPoint = world.getJumpPoint()
        steeringController.activate('arrive',
                                    jumpPoint.getPosition(),
                                    .6)
        
    @classmethod
    def execute(cls,
                owner):
        pass
    
    @classmethod
    def exit(cls,
             owner):
        pass
    
verify.verifyClass(statemachine.IState, EscapeToJumpPoint)

#Attackers

@implementer(statemachine.IState)
class AttackPursuingMotherShip(object):
    
    @classmethod
    def enter(cls,
              owner):
        steeringController = owner.getSteeringController()
        fleet = owner.fleet
        enemyFleet = fleet.getEnemyFleet()
        enemyMotherShip = enemyFleet.getMotherShip()
        steeringController.activate('pursue',
                                    enemyMotherShip)
        
    @classmethod
    def execute(cls,
                owner):
        pass
    
    @classmethod
    def exit(cls,
             owner):
        pass
    
    
verify.verifyClass(statemachine.IState, AttackPursuingMotherShip)


@implementer(statemachine.IState)
class FighterGlobalState(object):
    @classmethod
    def enter(cls,
              owner):
        pass
    
    @classmethod
    def execute(cls,
                owner):
        steeringStateMachine = owner.steeringStateMachine
        goalStateMachine = owner.goalStateMachine
        currentGoalState = goalStateMachine.currentState
        currentSteeringState = steeringStateMachine.currentState
        
        if currentGoalState is not ReturnToMotherShip and isCriticallyDamaged(owner):
            goalStateMachine.changeState(ReturnToMotherShip)
        
        elif currentGoalState is owner.mission:
            if owner.mission.isComplete(owner):
                goalStateMachine.changeState(EscortMotherShip)
            elif isUnderAttack(owner):
                goalStateMachine.changeState(EvadeAttack)
            
        elif currentGoalState is EvadeAttack:
            if not isUnderAttack(owner):
                goalStateMachine.changeState(owner.mission)
            elif owner.mission.isComplete(owner):
                goalStateMachine.changeState(EscortMotherShip) 
                
        elif currentGoalState is EscortMotherShip:
            if isUnderAttack(owner):
                goalStateMachine.changeState(EvadeAttack)
            elif not owner.mission.isComplete(owner):
                goalStateMachine.changeState(owner.mission) 
            
                
        
#        if stateCluster == 'Attack':
#            if isUnderAttack(owner):
#                if shotsFiredAtMe(owner):
#                    stateMachine.changeState(EvadeShots)
#                else:
#                    stateMachine.changeState(DefendMyself)
#            elif not getEligibleTargets(owner):
#                stateMachine.changeState(EscortMotherShip)
#        elif stateCluster == 'Evade':
#            if not getEligibleTargets(owner):
#                stateMachine.changeState(EscortMotherShip)
#            if not isUnderAttack(owner):
#                stateMachine.changeState(Dive)
#        elif stateCluster == 'Patrol':
#            if getEligibleTargets(owner):
#                stateMachine.changeState(Dive)
#            elif isUnderAttack(owner):
#                stateMachine.changeState(DefendMyself)
#                
    @classmethod
    def exit(cls,
             owner):
        pass

@implementer(statemachine.IState)
class EvadeAttack(object):
    @classmethod
    def enter(cls,
              owner):
        owner.setTargetingSystem(targetingsystem.TargetClosestAttackingFighter)
    
    @classmethod
    def execute(cls,
                owner):
        pass
    
    @classmethod
    def exit(cls,
             owner):
        pass

verify.verifyClass(statemachine.IState, FighterGlobalState)


@implementer(statemachine.IState)
class EscortMotherShip(object):
    
    @classmethod
    def enter(cls,
              owner):
        steeringController = owner.steeringController
        fleet = owner.fleet
        ourMotherShip = fleet.getMotherShip()
        steeringStates.plotLocalRouteAroundTarget(owner,
                                                  ourMotherShip)
        steeringController.activate('followpath',
                                    ourMotherShip)
    
    @classmethod
    def execute(cls,
                owner):
        target = owner.acquireTarget()
        if target:
            owner.goalStateMachine.changeState(owner.mission)
    
    @classmethod
    def exit(cls,
             owner):
        steeringController = owner.steeringController
        steeringController.deactivate('followpath')

verify.verifyClass(statemachine.IState, EscortMotherShip)


@implementer(statemachine.IState)
class FlightGroupState(object):
    @classmethod
    def enter(cls,
              owner):
        pass
    
    @classmethod
    def execute(cls,
                owner):
        pass
    
    @classmethod
    def exit(cls,
             owner):
        pass
        
verify.verifyClass(statemachine.IState, FlightGroupState)


@implementer(statemachine.IState)
class DestroyEnemyShip(object):
    @classmethod
    def enter(cls,
              owner):
        owner.targetingSystem = cls.targetingSystemClass
        steeringStateMachine = owner.steeringStateMachine
        steeringStateMachine.changeState(steeringStates.Dive)
        
    @classmethod
    def exit(cls,
             owner):
        pass
    
    @classmethod
    def execute(cls,
                owner):
        pass
        
    @classmethod
    def isComplete(cls, owner):
        return bool(owner.target)


class DestroyClosestEnemyCapitalShip(DestroyEnemyShip):
    targetingSystemClass = targetingsystem.TargetClosestEnemyCapitalShip

class DestroyGreatestThreatToMothership(DestroyEnemyShip):
    targetingSystemClass = targetingsystem.TargetGreatestThreatToMotherShip
    
class AttackEscapingMothership(DestroyEnemyShip):
    targetingSystemClass = targetingsystem.TargetEnemyMotherShip
    

@implementer(statemachine.IState)
class ReturnToMotherShip(object):
    @classmethod
    def enter(cls,
              owner):
        owner.steeringController.activate('pursue',
                                          owner.fleet.motherShip)
        
    @classmethod
    def exit(cls,
             owner):
        owner.steeringController.deactivate('arrive')
        
    @classmethod
    def execute(cls,
                owner):
        motherShip = owner.fleet.motherShip
        ownerPosition = owner.getPosition()
        targetPosition = motherShip.getPosition()
        ownerToTarget = calculate.subtractPoints(targetPosition,
                                                 ownerPosition)
        distanceSquaredToTarget = vector.getMagnitudeSquared(ownerToTarget)
        if distanceSquaredToTarget <= motherShip.hangarEntryThresholdSquared:
            motherShip.pickup(owner)
        
        
        
        
def isCriticallyDamaged(owner):
    if float(owner.health) / float(owner.totalHealth) < .25:
        return True
    else:
        return False
    
def isUnderAttack(owner):
    gunsTargetingOwner = owner.targettingTurrets
    return bool(gunsTargetingOwner)
    
def shotsFiredAtMe(owner):
    world = owner.world
    shots = world.shotsByTarget.get(owner, [])
    return shots
