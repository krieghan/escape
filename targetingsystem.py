from twodee.geometry import (calculate,
                             vector)

class NoTargeting:
    @classmethod
    def acquireTarget(cls,
                      owner):
        return None

class TargetEnemyMotherShip:
    @classmethod
    def acquireTarget(cls,
                      owner):
        fleet = owner.fleet
        enemyFleet = fleet.getEnemyFleet()
        enemyMotherShip = enemyFleet.getMotherShip()
        return enemyMotherShip 

class TargetClosestEnemyFighter:
    @classmethod
    def acquireTarget(cls,
                      owner):
        fleet = owner.fleet
        ownerPosition = owner.getPosition()
        enemyFleet = fleet.getEnemyFleet()
        closestShip = None
        closestDistanceSquared = None
        
        for enemy in enemyFleet.getAllFighters():
            enemyPosition = enemy.getPosition()
            ownerToEnemy = calculate.subtractPoints(enemyPosition,
                                                    ownerPosition)
            distanceSquaredToEnemy = vector.getMagnitudeSquared(ownerToEnemy)
            if closestShip is None or distanceSquaredToEnemy < closestDistanceSquared:
                closestShip = enemy
                closestDistanceSquared = distanceSquaredToEnemy
                
        return closestShip

#Bomber attacking mothership who is closest to *me*
class TargetClosestThreatToMotherShip:
    @classmethod
    def acquireTarget(cls,
                      owner):
        fleet = owner.fleet
        ownerPosition = owner.getPosition()
        enemyFleet = fleet.getEnemyFleet()
        closestShip = None
        closestDistanceSquared = None
        
        enemyBombers = enemyFleet.getAllFighters(shipType='bomber')
        for enemy in enemyBombers:
            enemyPosition = enemy.getPosition()
            ownerToEnemy = calculate.subtractPoints(enemyPosition,
                                                    ownerPosition)
            distanceSquaredToEnemy = vector.getMagnitudeSquared(ownerToEnemy)
            if closestShip is None or distanceSquaredToEnemy < closestDistanceSquared:
                closestShip = enemy
                closestDistanceSquared = distanceSquaredToEnemy
        
        return closestShip

class TargetGreatestThreatToMotherShip:
    @classmethod
    def acquireTarget(cls,
                      owner):
        fleet = owner.fleet
        motherShip = fleet.getMotherShip()
        motherShipPosition = motherShip.getPosition()
        
        enemyFleet = fleet.getEnemyFleet()
        closestShip = None
        closestDistanceSquared = None
        
        enemyBombers = enemyFleet.getAllFighters(shipType='bomber')
        for enemy in enemyBombers:
            enemyPosition = enemy.getPosition()
            motherShipToEnemy = calculate.subtractPoints(enemyPosition,
                                                         motherShipPosition)
            distanceSquaredToEnemy = vector.getMagnitudeSquared(motherShipToEnemy)
            if closestShip is None or distanceSquaredToEnemy < closestDistanceSquared:
                closestShip = enemy
                closestDistanceSquared = distanceSquaredToEnemy
        
        return closestShip
    
    

class TargetClosestEnemyCapitalShip:
    @classmethod
    def acquireTarget(cls,
                      owner):
        fleet = owner.fleet
        ownerPosition = owner.getPosition()
        enemyFleet = fleet.getEnemyFleet()
        enemyMotherShip = enemyFleet.getMotherShip()
        return enemyMotherShip
    
def findClosestEntity(owner, listOfEntities):
    ownerPosition = owner.getPosition()
    closestEntity = None
    closestDistanceSquared = None
    for entity in listOfEntities:
        entityPosition = entity.getPosition()
        entityToOwner = calculate.subtractPoints(entityPosition,
                                                 ownerPosition)
        distanceSquaredToOwner = vector.getMagnitudeSquared(entityToOwner)
        if closestEntity is None or distanceSquaredToOwner < closestDistanceSquared:
            closestEntity = entity
            closestDistanceSquared = distanceSquaredToOwner
            
    return closestEntity
        
class TargetClosestAttackingFighter:
    @classmethod
    def acquireTarget(cls,
                      owner):
        attackers = owner.attackers
        closestAttacker = findClosestEntity(owner, attackers)
        
        return closestAttacker