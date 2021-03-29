import events as e

from .vector import *
from .listSearch import *

import copy

import events as e
import settings as s

from random import shuffle
import numpy as np

from .Actions import *

INF_DISTANCE = s.COLS * s.ROWS * 1000
crateWall = 1
stoneWall = -1
freeTile = 0

timeCostDelayRewardForAction = {
    'LEFT': 1,
    'WAIT': 1,
    'RIGHT': 1,
    'UP': 1,
    'DOWN': 1,
    'BOMB': 0
}

RewardActionForNecessaryTimeToKll = {
    'LEFT': 0,
    'WAIT': 0,
    'RIGHT': 0,
    'UP': 0,
    'DOWN': 0,
    'BOMB': 1
}

def GeneratePositionIfCrateFound(field, position):

    if(field[position[0], position[1]] == crateWall):
        return True
    else:
        return False

# Function modified from items.py
def ComputeFutureExplosionZoneForPosition(x, y, field, timer, power = s.BOMB_POWER):
    """
     0 / 1 field map positions are affected
     -1 ( stone ) it's a stopper 
    """

    FutureExplosion = [(x, y, timer)]

    for i in range(1, power+1):
        if field[x+i, y] == -1:
            break
        if field[x + i, y] in [0, 1]:
            FutureExplosion.append((x+i, y, timer))
        if field[x + i, y] == 1:
            break
    for i in range(1, power+1):
        if field[x-i, y] == -1:
            break
        if field[x - i, y] in [0, 1]:
            FutureExplosion.append((x-i, y, timer))
        if field[x - i, y] == 1:
            break
    for i in range(1, power+1):
        if field[x, y+i] == -1:
            break
        if field[x, y + i] in [0, 1]:
            FutureExplosion.append((x, y+i, timer))
        if field[x, y + i] == 1:
            break
    for i in range(1, power+1):
        if field[x, y-i] == -1:
            break
        if field[x, y - i] in [0, 1]:
            FutureExplosion.append((x, y-i, timer))
        if field[x, y - i] == 1:
            break

    return FutureExplosion


def ComputeFutureCrateWallExplodedForPosition(position, field, power=s.BOMB_POWER):

    """
     0 / 1 field map positions are affected
     -1 ( stone ) it's a stopper 
    """

    #(x, y, timer)
    FutureExplosion = []
    (x, y) = position

    for i in range(1, power+1):
        if field[x+i, y] in [stoneWall, crateWall]:
            if field[x+i, y] == crateWall:
                FutureExplosion.append((x+i, y, 1))
            break

    for i in range(1, power+1):
        if field[x-i, y] in [stoneWall, crateWall]:
            if field[x-i, y] == crateWall:
                FutureExplosion.append((x-i, y, 1))
            break

    for i in range(1, power+1):
        if field[x, y+i] in [stoneWall, crateWall]:
            if field[x, y+i] == crateWall:
                FutureExplosion.append((x, y+i, 1))
            break

    for i in range(1, power+1):
        if field[x, y-i] in [stoneWall, crateWall]:
            if field[x, y-i] == crateWall:
                FutureExplosion.append((x, y-i, 1))
            break

    return FutureExplosion


def chanceToKill(position, field, otherPlayersPosition, power=s.BOMB_POWER):

    #(x, y, timer)
    FutureExplosion = []
    (x, y) = position
    
    chance = 0

    for i in range(1, power+1):
        if field[x+i, y] in [stoneWall, crateWall]:
            break
        if (x+i, y) in otherPlayersPosition:
            chance += (power-i+1)

    for i in range(1, power+1):
        if field[x-i, y] in [stoneWall, crateWall]:
            break
        if (x-i, y) in otherPlayersPosition:
            chance += (power-i+1)

    for i in range(1, power+1):
        if field[x, y+i] in [stoneWall, crateWall]:
            break
        if (x, y+i) in otherPlayersPosition:
            chance += (power-i+1)

    for i in range(1, power+1):
        if field[x, y-i] in [stoneWall, crateWall]:
            break
        if (x, y-i) in otherPlayersPosition:
            chance += (power-i+1)

    return chance

def FindSafestSmallestDistanceToCrateWall(
        position, searchedForSet, game_state: set, explosionsMap,
        futureExplosionList, bombs_xy, otherPlayersPosition = []):

    initialDistance = 1

    queue = [(position[0], position[1], initialDistance)]
    checked = set()
    while queue:
        pos_x, pos_y, distance = queue.pop(0)
        if (pos_x, pos_y) in checked:
            continue
        checked.add((pos_x, pos_y))
        neighbors_test = getLegalNeighborsForPositionCureentPositionIncluded(
            (pos_x, pos_y), ["WAIT", "UP", "DOWN", "LEFT", "RIGHT"])
        for neighbor in neighbors_test:
            if neighbor in searchedForSet:
                return distance
        listLegalActions = getLegalAndSafeActionForPositionAtEpisodStep(
            (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition)
        neighbors = getLegalNeighborsForPosition((pos_x, pos_y), listLegalActions)
        for nbr_x, nbr_y in neighbors:
            queue.append((nbr_x, nbr_y, distance + 1))

    # when no feasible ( legal and SAFE!!! ) path can be found the reward must be 0 or as small as possible
    return INF_DISTANCE




def FindSafestSmallestDistanceToSet(
        position, searchedForSet, game_state: set, explosionsMap,
        futureExplosionList, bombs_xy, otherPlayersPosition = []):

    initialDistance = 1

    queue = [(position[0], position[1], initialDistance)]
    checked = set()
    while queue:
        pos_x, pos_y, distance = queue.pop(0)
        if (pos_x, pos_y) in checked:
            continue
        checked.add((pos_x, pos_y))
        if (pos_x, pos_y) in searchedForSet and \
                checkForLegalNoBlastNoFutureExplosionForPositionAtEpisodStep(
                    (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, otherPlayersPosition):
            return distance
        listLegalActions = getLegalAndSafeActionForPositionAtEpisodStep(
            (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition)
        neighbors = getLegalNeighborsForPosition((pos_x, pos_y), listLegalActions)
        for nbr_x, nbr_y in neighbors:
            queue.append((nbr_x, nbr_y, distance + 1))

    # when no feasible ( legal and SAFE!!! ) path can be found the reward must be 0 or as small as possible
    return INF_DISTANCE


def FindSafestSmallestDistanceToCratesWithSafePathDeparture(
        position, game_state: set, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition = []):

    field = game_state["field"]

    initialDistance = 1

    queue = [(position[0], position[1], initialDistance)]
    checked = set()

    while queue:
        pos_x, pos_y, distance = queue.pop(0)
        if (pos_x, pos_y) in checked:
            continue
        checked.add((pos_x, pos_y))
        neighboarCrates = [(pos_x + pos[0], pos_y + pos[0]) for pos in directionsAsList
                           if GeneratePositionIfCrateFound(field, (pos_x + pos[0], pos_y + pos[1]))]
        if len(neighboarCrates) > 0:
            departureDistanceToSafe = FindSafestSmallestDistanceToSecurePosition(
                (pos_x, pos_y),
                game_state,
                explosionsMap,
                futureExplosionList + [(pos_x, pos_y, 3)],
                bombs_xy,
                otherPlayersPosition)
            if departureDistanceToSafe != INF_DISTANCE:
                return distance
        listLegalActions = getLegalAndSafeActionForPositionAtEpisodStep(
            (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition)
        neighbors = getLegalNeighborsForPosition((pos_x, pos_y), listLegalActions)
        for nbr_x, nbr_y in neighbors:
            queue.append((nbr_x, nbr_y, distance + 1))

    # when no feasible ( legal and SAFE!!! ) path can be found the reward must be 0 or as small as possible
    return INF_DISTANCE




def FindSafestSmallestDistanceToSecurePosition(
        position, game_state: set, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition = []):

    initialDistance = 1

    queue = [(position[0], position[1], initialDistance)]
    checked = set()

    while queue:
        pos_x, pos_y, distance = queue.pop(0)
        if (pos_x, pos_y) in checked:
            continue
        checked.add((pos_x, pos_y))
        if checkForLegalNoBlastNoFutureExplosionForPositionAtEpisodStep(
                (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, otherPlayersPosition):
            return distance
        listLegalActions = getLegalAndSafeActionForPositionAtEpisodStep(
            (pos_x, pos_y), game_state, distance, explosionsMap, futureExplosionList, bombs_xy, otherPlayersPosition)
        neighbors = getLegalNeighborsForPosition((pos_x, pos_y), listLegalActions)
        for nbr_x, nbr_y in neighbors:
            queue.append((nbr_x, nbr_y, distance + 1))

    # when no feasible ( legal and SAFE!!! ) path can be found the reward must be 0 or as small as possible
    # for that one must return big a distance
    return INF_DISTANCE




class IdentityExtractor:
    def getFeatures(self, state, action):

        bias = 1;

        (n, s, b, (x, y)) = state['self']


        coin_found = (isCointAt(state['coins'],x,y))

        # position / coin
        feats = vector([bias, x, y, coin_found])

        return feats

    def getNumberOf(self):
        return 4;


# Function modified from items.py
def get_blast_coords(arena, x, y):
    """Retrieve the blast range for a bomb.
    The maximal power of the bomb (maximum range in each direction) is
    imported directly from the game settings. The blast range is
    adjusted according to walls (immutable obstacles) in the game
    arena.
    Parameters:
    * arena:  2-dimensional array describing the game arena.
    * x, y:   Coordinates of the bomb.
    Return Value:
    * Array containing each coordinate of the bomb's blast range.
    """
    bomb_power = s.BOMB_POWER
    blast_coords = [(x, y)]

    for i in range(1, bomb_power+1):
        if arena[x+i, y] == -1: break
        blast_coords.append((x+i, y))
    for i in range(1, bomb_power+1):
        if arena[x-i, y] == -1: break
        blast_coords.append((x-i, y))
    for i in range(1, bomb_power+1):
        if arena[x, y+i] == -1: break
        blast_coords.append((x, y+i))
    for i in range(1, bomb_power+1):
        if arena[x, y-i] == -1: break
        blast_coords.append((x, y-i))

    return blast_coords

class FeatureExtractor:

    FeaturesForStateAndAction = {}

    def getFeatures(self, game_state, action):
        round = None
        step = None
        if game_state != None and action != None:
            round = game_state.get('round')
            step = game_state.get('step')
        val = FeatureExtractor.FeaturesForStateAndAction.get((round, step, action))
        if val == None:
            return ones(self.getNumberOf())
        return val

    def NormalizeActionsForState(self, game_state):
        round = game_state['round']
        step = game_state['step']
        for featureIdx in range(1, self.getNumberOf() ):
            sum = 0
            for action in getLegalActionsForAgent(game_state):
                sum += FeatureExtractor.FeaturesForStateAndAction[(round, step, action)][featureIdx]
            if sum != 0:
                for action in getLegalActionsForAgent(game_state):
                    FeatureExtractor.FeaturesForStateAndAction[(round, step, action)][featureIdx] /= float(sum)
            else:
                for action in getLegalActionsForAgent(game_state):
                    FeatureExtractor.FeaturesForStateAndAction[(round, step, action)][featureIdx] = \
                        float(1) / len(getLegalActionsForAgent(game_state))



    def ComputeAndNormalizeFeaturesForAllLegalActionsFor(self, game_state):
        round = game_state['round']
        step = game_state['step']
        for action in getLegalActionsForAgent(game_state):
            features = self.ComputeFeaturesFor(game_state, action)
            FeatureExtractor.FeaturesForStateAndAction[(round, step, action)] = features
        self.NormalizeActionsForState(game_state)

        # print("ComputeAndNormalizeFeaturesForAllLegalActionsFor ")
        # for action in getLegalActionsForAgent(game_state):
        #     print(
        #         "round: ", round,
        #         "step: ", step,
        #         "action: ", action,
        #         "feature: ", FeatureExtractor.FeaturesForStateAndAction[(round, step, action)])

    def ComputeFeaturesFor(self, game_state, action):

        self.game_state = game_state

        #game round
        self.round = game_state['round']

        #stepCurrentEpisod
        self.stepCurrentEpisod = game_state['step']

        # 1 for crates / -1 for stone walls / 0 for free tiles
        # np.array [][] [ 0,shape_x ) [0, shape_y )
        self.field = game_state["field"]

        #size of the field [ 0,shape_x ) [0, shape_y )
        (self.field_shape_X, self.field_shape_Y) = self.field.shape

        # list of ( ( X, Y ), timer ) 'timer' is in [0,3] e.g.: 4 steps until explode
        #in update for
        self.bombs = game_state['bombs']

        self.bombs_xy = [(x, y) for ((x, y), _) in game_state['bombs']]

        # list of ( x, y ) coordinates
        self.coins = game_state['coins']

        #np.array [][] [ 0,shape_x ) [0, shape_y )
        # 0  no explosion
        self.explosionsMap = game_state['explosion_map']

        # list of (str, int, bool, (int, int)) -> name / score / bomb available / ( x,y ) - coordinates
        self.others = game_state['others']

        # list of (x, y) positions of the other agents ( for generic search )
        self.others_xy = [other_xy for (_, __, ___, other_xy) in game_state['others']]

        #agent
        (
            self.AgentName,
            self.currentScore,
            self.bombsAvailable,
            (self.AgentPositionX, self.AgentPositionY)
        ) = game_state['self']

        self.AgentStruct = game_state['self']

        self.bias = 1

        self.Agent = (self.AgentPositionX, self.AgentPositionY)

        self.AgentPosAfterAction = {
            'BOMB': (self.AgentPositionX, self.AgentPositionY),
            'WAIT': (self.AgentPositionX, self.AgentPositionY),
            'UP'   : (self.AgentPositionX, self.AgentPositionY - 1),
            'DOWN' : (self.AgentPositionX, self.AgentPositionY + 1),
            'LEFT' : (self.AgentPositionX - 1, self.AgentPositionY),
            'RIGHT': (self.AgentPositionX + 1, self.AgentPositionY),
        }

        #list of (x, y, timer) future affected tiles with there coresponding timers
        self.futureExplosionList = []

        for bomb in self.bombs:
            ((x, y), timer) = bomb
            self.futureExplosionList += ComputeFutureExplosionZoneForPosition(x, y, self.field, timer)

        self.cratesList = []
        self.absolutSafePositions = []
        #if free tiles
        #if no bomb
        #if no player
        #if no other
        #if no explosion
        #if no coins
        for i in range(0, self.field_shape_X):
            for j in range(0, self.field_shape_Y):
                #for self.absolutSafePositions
                if self.field[i][j] == 0 and \
                        (not (i, j) in self.bombs_xy) and \
                        (not (i, j) == self.Agent) and \
                        (not (i, j) in self.others_xy) and \
                        self.explosionsMap[i][j] == 0 and \
                        (not (i, j) in self.coins):
                    self.absolutSafePositions.append((i, j))
                #for self.cratesList
                if self.field[i][j] == crateWall:
                    self.cratesList.append((i, j))


        # for i in range(0, self.field_shape_X):
        #     for j in range(0, self.field_shape_Y):
        #         if self.field[i][j] == crateWall:
        #             self.cratesList.append((i, j))

        aux = vector([
            self.bias,
            self.Feature1_Alex(action),
            self.Feature2_Alex(action),
            self.Feature2_Alex_bis(action),
            self.Feature3_Alex(action),
            self.Feature3_Alex_bis(action),
            self.Feature4_Alex(action),
            #self.Feature6_Alex(action),
            #self.Feature6_Alex_bis(action),
            self.Feature6_Alex_bis_bis(action),
            self.Feature_destroyCrateWall(action)
        ])
        #print("Action: ", action, "Feature: ", aux)
        return aux

    def getNumberOf(self):
        return 9



    def Feature1_Alex(self, action):
        """
        Reward the agent proportional with the smallest distance towards a coin after taking
        a specific action from a specific location and a specific game configuration.
        The path is considered legal ( no step is taken through walls, bombs or other adversaries)
        and safe ( no bomb explosion is taken place on neither of the positions of the trajectory
        discovered at the specific moment when the agent is moving by. It also takes into consideration
        the possibility that the action to be dropping a bomb.

        The path is computed using a modified version of breadth-first search which taken
        into consideration also the explosion time of each bomb starting from that moment forward.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)


        distance = INF_DISTANCE

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    _, #start position
                    self.coins,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,#if action='BOMB'
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'], #if action='BOMB',
                    self.others
                )

        #print("stepCurrentEpisod: ", self.stepCurrentEpisod, "distance: ", distance, "action: ", action)
        result = float(5) / (distance)
        #result = 15 - float(self.stepCurrentEpisod) / (distance)
        return result

    def Feature2_Alex(self, action):
        """
        Reward the agent proportional with the smallest distance towards a safe location after
        taken a specific action for a specific location and a specific game configuration.
        Each element of the path is considered legal and safe at the time when the agent is
        passing by as explained in Feature 1.

        The path is computed using a modified version of breadth-first search which taken
        into consideration also the explosion time of each bomb starting from that moment forward.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)


        distance = INF_DISTANCE

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSecurePosition(
                    _, #start position
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'], #if action='BOMB'
                    self.others
                )

        distance -= 1
        #print("stepCurrentEpisod: ", self.stepCurrentEpisod, "distance: ", distance, "action: ", action)
        #result = float(4) / (distance)
        #return float(4)/distance

        #if distance == 0:
        #    return INF_DISTANCE
        #return float(1) / distance

        reward = s.BOMB_TIMER - distance
        if reward < 0:
            return 0
        else:
            return reward

    def Feature2_Alex_bis(self, action):
        """
        Reward the agent equally for the actions ( for a specific location and a specific configuration )
        that have as a result positions that are part of paths towards safe locations in a safe
        and legal way as described in Feature 1 regardless of the length of those.

        Same as in Feature 1 and Feature 2, the computation is done using a modified version of
        breadth-first search.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)


        distance = INF_DISTANCE

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSecurePosition(
                    _, #start position
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'], #if action='BOMB'
                    self.others
                )

        distance -= 1
        #print("stepCurrentEpisod: ", self.stepCurrentEpisod, "distance: ", distance, "action: ", action)
        #result = float(4) / (distance)
        #return float(4)/distance

        #if distance == 0:
        #    return INF_DISTANCE
        #return float(1) / distance

        if distance != INF_DISTANCE:
            return 1

        return 0

    def Feature3_Alex(self, action):
        """
        Reward the agent proportional with the inverse of the smallest distance towards
        another agent after taking the action. ( for a specific location and a specific
        game configuration ) The path is legal and safe. ( as explained in Feature 1)

        In case no agent is reachable the reward is 0.
        The path is computed using a modified version of breadth-first search.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        distance = INF_DISTANCE

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    _, #start position
                    self.others_xy,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'],#if action='BOMB',
                    [] #no other players for this search
                )

        #print("stepCurrentEpisod: ", self.stepCurrentEpisod, "distance: ", distance, "action: ", action)
        result = float(10) / (distance)
        #result =  8 - float(5) / (distance)
        #result = float(self.stepCurrentEpisod) / (distance)
        return result

    def Feature3_Alex_bis(self, action):

        """
        Reward the agent by how good is the future position, corresponding to the action,
        for killing the other agents.

        The computation is done by a fill-algorithm that checks whether for the new position
        ( for corresponding game configuration ) the corresponding blast will overlap with
        any of the other agent's positions. The score takes into account also the distance
        and offers an extra reward to bombing action as its result will be sooner.

        The result of the action is first checked to be legal and safe as described in Feature 1.
        """


        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        chance = 0

        distance = INF_DISTANCE
        
        if action in listLegalAndSafeAction:


            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    _, #start position
                    self.coins + self.others_xy,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,#if action='BOMB'
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'], #if action='BOMB',
                    self.others
                )
            if distance < INF_DISTANCE:
                chance = chanceToKill(
                    (
                        self.AgentPositionX + directionsFromStrings[action][0],
                        self.AgentPositionY + directionsFromStrings[action][1]
                    ),
                    self.field,
                    self.others_xy)

                if chance != 0:
                    chance + RewardActionForNecessaryTimeToKll[action]

                return chance

        return chance

    def Feature4_Alex(self, action):
        """
        Reward the agent by how big is the chance that the other agents will die
        in the new game configuration as a result of some action taken for a specific
        location on the map.

        The computation takes into account the number of the legal and safe positions
        for the other players at some specific episode step (the first step after the action )
        as defined in Feature 1.

        The reward takes into account also whether the action is legal and safe too.
        """

        NumberOfUsafePositions = 0

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                for OtherPlayer in self.others_xy:
                    NumberOfUsafePositions += not checkForLegalNoBlastNoFutureExplosionForPositionAtEpisodStep(
                        OtherPlayer, #check OtherPlayer's position
                        self.game_state,
                        1,
                        self.explosionsMap,
                        self.futureExplosionList + extraFutureExplosions,
                        #extract 'OtherPlayer' and add 'Agent' in 'others' list
                        [(_, __, ___, other) for (_, __, ___, other) in self.others if other != OtherPlayer] +
                        [(
                            self.AgentName,
                            self.currentScore,
                            self.bombsAvailable,
                            (self.AgentPositionX + directionsFromStrings[action][0],
                             self.AgentPositionY + directionsFromStrings[action][1]))]
                    )

        return NumberOfUsafePositions

    "not used!"
    def Feature5_Alex(self, action):
        """
        Reward the agent proportional with the smallest distance
        after taking the 'action' ( legal and SAFE!!! ) in a direction towards another agent
        """
        pass

    "not used"
    def Feature6_Alex(self, action):
        """
        Reward the agent proportional with the smallest distance
        after taking the 'action' ( legal and SAFE!!! ) in a direction towards a "tile"
        that also offers a safe departure
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        result = INF_DISTANCE

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for __ in neighbor:  # just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(__[0], __[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    __,  # start position
                    self.coins + self.others_xy + self.absolutSafePositions,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,  # if action='BOMB'
                    self.bombs_xy + [(__[0], __[1]) for _ac in [action] if _ac == 'BOMB'],  # if action='BOMB',
                    self.others
                )

            if distance < INF_DISTANCE:
                crateWallpossibleDestroyedList = ComputeFutureCrateWallExplodedForPosition(__, self.field)

                # if we are already close enough by some crate
                #if len(crateWallpossibleDestroyedList) > 0:
                #    return 1 + RewardActionForNecessaryTimeToKll[action]*2

                neighbor = getLegalNeighborsForPositionCureentPositionIncluded(
                    (self.AgentPositionX, self.AgentPositionY),
                    [action])

                for _ in neighbor: #just one neighbor coresponding to "action"

                    result = FindSafestSmallestDistanceToCratesWithSafePathDeparture(
                        _, self.game_state, self.explosionsMap, self.futureExplosionList, self.bombs_xy, self.others)

                return float(5) / result + 1 - timeCostDelayRewardForAction[action]

        #print("6_Alex ", "step:", self.stepCurrentEpisod, "action: ", action, float(5) / result)
        return float(5) / result

    "not used"
    def Feature6_Alex_bis(self, action):
        """
        Reward proportional with the chance that current "action" increase the chance of tile/crateWall destruction
        as soon as possible
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        if action in listLegalAndSafeAction:

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for __ in neighbor:  # just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(__[0], __[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    __,  # start position
                    self.coins + self.others_xy + self.absolutSafePositions,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,  # if action='BOMB'
                    self.bombs_xy + [(__[0], __[1]) for _ac in [action] if _ac == 'BOMB'],  # if action='BOMB',
                    self.others
                )
            if distance < INF_DISTANCE:

                crateWallpossibleDestroyedList = ComputeFutureCrateWallExplodedForPosition(
                    (
                        self.AgentPositionX + directionsFromStrings[action][0],
                        self.AgentPositionY + directionsFromStrings[action][1]),
                    self.field)

                sumCrate = 0
                for wall in crateWallpossibleDestroyedList:
                    (_, _, value) = wall
                    sumCrate += value

                if sumCrate > 0:
                    sumCrate += RewardActionForNecessaryTimeToKll[action]
                return sumCrate

            #print("6_Alex_bis: ", "step: ", self.stepCurrentEpisod, "action: ", action, result)

        return 0  #len(crateWallpossibleDestroyedList)

    def Feature6_Alex_bis_bis(self, action):
        """
        Reward the agent if the result of the action for the current position
        and current game configuration results in decreasing the distance to some crate tile wall.

        The computation is done by taking the difference between the shortest distance
        ( computed in a legal and safe way by a version of breadth-first search ) towards a
        crate tile calculated from the current position and also the distance from the position
        the agent ends up as a result of the action.

        The output is 1 if the distance is shorter and 0 otherwise.

        The computation takes into account also whether the new position is legal and safe too.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        distance_newPosition = INF_DISTANCE

        if action in listLegalAndSafeAction:

            distanceToCoin = FindSafestSmallestDistanceToSet(
                self.Agent,  # start position
                self.coins,
                self.game_state,
                self.explosionsMap,
                self.futureExplosionList,  # if action='BOMB'
                self.bombs_xy,
                self.others
            )
            if distanceToCoin < INF_DISTANCE:
                return 0

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for _ in neighbor: #just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(_[0], _[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    _,  # start position
                    self.coins + self.others_xy + self.absolutSafePositions,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,  # if action='BOMB'
                    self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'],  # if action='BOMB',
                    self.others
                )
                if distance < INF_DISTANCE:

                    distance_newPosition = FindSafestSmallestDistanceToCrateWall(
                        _, #start position
                        self.cratesList,
                        self.game_state,
                        self.explosionsMap,
                        self.futureExplosionList + extraFutureExplosions,
                        self.bombs_xy + [(_[0], _[1]) for _ac in [action] if _ac == 'BOMB'],#if action='BOMB',
                        self.others
                    )

                    distance_currentPosition = FindSafestSmallestDistanceToCrateWall(
                        self.Agent, #start position
                        self.cratesList,
                        self.game_state,
                        self.explosionsMap,
                        self.futureExplosionList,
                        self.bombs_xy,
                        self.others
                    )

                    if distance_currentPosition > distance_newPosition:
                        return 1

        return 0

    def Feature_destroyCrateWall(self, action):
        """
        Reward the agent if the current action has as immediate result crate walls distraction.
        This will reward only the bomb action and punish all the other actions.
        The computation is done by using a fill-like algorithm to verify whether the blast from
        the current position is intersecting with any crate.

        The output is 1 if yes and 0 if no.
        The computation also takes into consideration whether the result of the action is safe
        and whether a coin is reachable in a safe and legal way.
        """

        listLegalAndSafeAction = getLegalAndSafeActionForPositionAtEpisodStep(
            (self.AgentPositionX, self.AgentPositionY),
            self.game_state,
            0, #NrEpisodStepsInTheFuture
            self.explosionsMap,
            self.futureExplosionList,
            self.bombs_xy,
            self.others)

        if action in listLegalAndSafeAction:

            distanceToCoin = FindSafestSmallestDistanceToSet(
                self.Agent,  # start position
                self.coins,
                self.game_state,
                self.explosionsMap,
                self.futureExplosionList,
                self.bombs_xy,
                self.others
            )
            if distanceToCoin < INF_DISTANCE:
                return 0

            neighbor = getLegalNextPositionsAfterLegalActions(
                (self.AgentPositionX, self.AgentPositionY),
                [action])

            for __ in neighbor:  # just one neighbor coresponding to "action"

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(__[0], __[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    __,  # start position
                    self.coins + self.others_xy + self.absolutSafePositions,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,  # if action='BOMB'
                    self.bombs_xy + [(__[0], __[1]) for _ac in [action] if _ac == 'BOMB'],  # if action='BOMB',
                    self.others
                )
            if distance < INF_DISTANCE:

                extraFutureExplosions = []
                if action == 'BOMB':
                    extraFutureExplosions = ComputeFutureExplosionZoneForPosition(__[0], __[1], self.field, 3)

                distance = FindSafestSmallestDistanceToSet(
                    __,  # start position
                    self.coins + self.others_xy + self.absolutSafePositions,
                    self.game_state,
                    self.explosionsMap,
                    self.futureExplosionList + extraFutureExplosions,  # if action='BOMB'
                    self.bombs_xy + [(__[0], __[1]) for _ac in [action] if _ac == 'BOMB'],  # if action='BOMB',
                    self.others
                )
            if distance < INF_DISTANCE:

                if action == 'BOMB':

                    crateWallpossibleDestroyedList_CurrentPosition = ComputeFutureCrateWallExplodedForPosition(
                        (
                            self.AgentPositionX,
                            self.AgentPositionY
                        ),
                        self.field)
                    if len(crateWallpossibleDestroyedList_CurrentPosition) > 0:
                        return 1


                # crateWallpossibleDestroyedList_NewPosition = ComputeFutureCrateWallExplodedForPosition(
                #     (
                #         self.AgentPositionX + directionsFromStrings[action][0],
                #         self.AgentPositionY + directionsFromStrings[action][1]),
                #     self.field)
                #
                # sumCrate_NewPosition = 0
                # for wall in crateWallpossibleDestroyedList_NewPosition:
                #     (_, _, value) = wall
                #     sumCrate_NewPosition += value
                #
                # crateWallpossibleDestroyedList_CurrentPosition = ComputeFutureCrateWallExplodedForPosition(
                #     (
                #         self.AgentPositionX,
                #         self.AgentPositionY
                #     ),
                #     self.field)
                #
                # sumCrate_CurrentPosition = 0
                # for wall in crateWallpossibleDestroyedList_NewPosition:
                #     (_, _, value) = wall
                #     sumCrate_CurrentPosition += value
                #
                # if sumCrate_NewPosition > sumCrate_CurrentPosition:
                #     return 1

            #print("6_Alex_bis: ", "step: ", self.stepCurrentEpisod, "action: ", action, result)

        return 0  #len(crateWallpossibleDestroyedList)

    def Feature7_Alex(self, action):
        """
        Reward the agent proportional with the smallest distance
        after taking the 'action' ( NOT NECESSARY legal and  NOT NECESSARY SAFE path!!! )
        in a direction towards a coin
        """
        pass

    def Feature8_Alex(self, action):
        """
        Reward the agent for suicide proportional with the chance the leading agent ( with a way bigger
        score ) to die after taking action "action". :D
        """

    def Feature9_Alex(self, action):
        """
        Reward the agent for ending up in a position/taking a decision that will decrease
        the chance of another agent to stay alive / get to a safe zone.
        """
        pass
