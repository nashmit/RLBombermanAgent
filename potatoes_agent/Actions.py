from .listSearch import *

directions = {
    (-1, 0): 'LEFT',
    (0, 0): 'WAIT',
    (1, 0): 'RIGHT',
    (0, -1): 'UP',
    (0, 1): 'DOWN'
}

directionsFromStrings = {
    'LEFT': (-1, 0),
    'WAIT': (0, 0),
    'RIGHT': (1, 0),
    'UP': (0, -1),
    'DOWN': (0, 1),
    'BOMB': (0, 0)
}

ACTIONS = ['UP', 'RIGHT', 'DOWN', 'LEFT', 'WAIT', 'BOMB']

directionsAsList = [(-1, 0), (0, 0), (1, 0), (0, 1), (0, -1)]


# must be improved!!!!! you can enter into a bomb range and still be safe!!!
def NoBomb( i, j, bombs, explosion_map, boardSizeX, boardSizeY, distance, direction, maxDistance, field):
    # in range
    if i in range(0, boardSizeX + 1) or j in range(0, boardSizeY + 1):
        return True

    # free tile
    if field[i][j] != 0:
        return True

    if distance <= maxDistance:
        if not isBombAt(bombs, i, j):
            if direction == 'N':
                return NoBomb(i, j - 1, bombs, explosion_map, boardSizeX, boardSizeY, distance + 1, direction)
            if direction == 'S':
                return NoBomb(i, j + 1, bombs, explosion_map, boardSizeX, boardSizeY, distance + 1, direction)
            if direction == 'E':
                return NoBomb(i + 1, j, bombs, explosion_map, boardSizeX, boardSizeY, distance + 1, direction)
            if direction == 'V':
                return NoBomb(i - 1, j, bombs, explosion_map, boardSizeX, boardSizeY, distance + 1, direction)
        else:
            return True;


def NoBombFindPath( i, j, bombs, explosion_map, boardSizeX, boardSizeY,
                   distance, maxDistance, direction, changedDirection, field):
    if not i in range(0, boardSizeX + 1) or not j in range(0, boardSizeY + 1):
        return False

    # free tile
    if field[i][j] != 0:
        return False

    if distance <= maxDistance:
        if not isBombAt(bombs, i, j):
            if changedDirection:
                return True;
            return \
                NoBombFindPath(i, j - 1, bombs, explosion_map, boardSizeX, boardSizeY,
                                    distance + 1, maxDistance, 'UP', 'UP' == direction, field) or \
                NoBombFindPath(i, j + 1, bombs, explosion_map, boardSizeX, boardSizeY,
                                    distance + 1, maxDistance, 'DOWN', 'DOWN' == direction, field) or \
                NoBombFindPath(i + 1, j, bombs, explosion_map, boardSizeX, boardSizeY,
                                    distance + 1, maxDistance, 'RIGHT', 'RIGHT' == direction, field) or \
                NoBombFindPath(i - 1, j, bombs, explosion_map, boardSizeX, boardSizeY,
                                    distance + 1, maxDistance, 'LEFT', 'LEFT' == direction, field)
        else:
            return False
    else:
        if not isBombAt(bombs, i, j):
            return True
        else:
            return False


def SafeToDropBombAtPosition(i, j, bombs, explosion_map, field):
    (boardSizeX, boardSizeY) = explosion_map.shape

    return \
        NoBombFindPath(i, j - 1, bombs, explosion_map, boardSizeX, boardSizeY, 0, 4, 'UP', False, field) or \
        NoBombFindPath(i, j + 1, bombs, explosion_map, boardSizeX, boardSizeY, 0, 4, 'DOWN', False, field) or \
        NoBombFindPath(i + 1, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 4, 'RIGHT', False, field) or \
        NoBombFindPath(i - 1, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 4, 'LEFT', False, field)


def BombExplosionFreePosition(self, i, j, bombs, explosion_map, field):
    (boardSizeX, boardSizeY) = explosion_map.shape
    if self.NoBomb(i, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 'N', 3, field) and \
            NoBomb(i, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 'S', 3, field) and \
            NoBomb(i, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 'E', 3, field) and \
            NoBomb(i, j, bombs, explosion_map, boardSizeX, boardSizeY, 0, 'V', 3, field):
        return True
    return False

#return True/False
#STRONG satety ( NO explosion and future explosion for position at EpisodStep)
#(timer - NrEpisodStepsInTheFuture is unsafe for [-2, -1] and [0,3] and safe only for [-inf, -3])
def checkForLegalNoBlastNoFutureExplosionForPositionAtEpisodStep(
        position, game_state: dict, NrEpisodStepsInTheFuture, explosionsMap, futureExplosionList, otherPlayers):

    okPosition = []

    (x, y) = (position[0], position[1])

    # accesible game board elements
    field = game_state["field"]
    (boardSizeX, boardSizeY) = field.shape

    # inside map
    # NO crates and NO stones
    # No current explosions active at EpisodStep
    # NO part of future blast region at EpisodStep
    # NO other player
    noMove = [(0, 0)]
    for (i, j) in noMove:
        if x + i in range(0, boardSizeX + 1) and y + j in range(0, boardSizeY + 1) and\
                field[x + i][y + j] == 0 and\
                explosionsMap[x + i][y + j] - NrEpisodStepsInTheFuture <= 0:
                futureExplosionActiveOrActiveInFuture = [timer - NrEpisodStepsInTheFuture
                                                         for (x_a, y_a, timer) in futureExplosionList
                                                         if (x_a, y_a) == (x+i, y+j) and
                                                         (timer - NrEpisodStepsInTheFuture in range(-2, 3+1))]
                otherPlayersAtPosition = [(x+i, y+j) for (_, __, ___, other_Player) in otherPlayers
                                          if other_Player == (x+i, y+j)]
                #must revisit this!!!
                #this should be true only for NrEpisodStepsInTheFuture==0
                #for NrEpisodStepsInTheFuture > 0, some probability must w.r.t. otherPlayer position be involved
                if len(futureExplosionActiveOrActiveInFuture) == 0 and len(otherPlayersAtPosition) == 0:
                    okPosition.append((i, j))

    return len(okPosition) > 0



#considering weak safety
#(timer - NrEpisodStepsInTheFuture is unsafe for [-2, -1] and safe for [0, 3] and [-inf, -3])
def getLegalAndSafeActionForPositionAtEpisodStep(
        position, game_state: dict, NrEpisodStepsInTheFuture,
        explosionsMap, futureExplosionList, bombs_xy, otherPlayers):

    legalActions = []

    legalNextPositions = []

    # user state
    (name, currentScore, bombActionPossible, (x, y)) = game_state["self"]

    gameEpisodStep = game_state['step']

    #overwritten (x, y) with "position" !!!!!!
    #same algorithm now!!!!
    (x, y) = (position[0], position[1])

    # accesible game board elements
    field = game_state["field"]
    (boardSizeX, boardSizeY) = field.shape

    # inside map
    # NO crates and NO stones
    # No current explosions active at EpisodStep
    # NO part of future blast region at EpisodStep
    # NO other player
    # NO bomb there
    for (i, j) in directionsAsList:
        if x + i in range(0, boardSizeX + 1) and y + j in range(0, boardSizeY + 1) and\
                field[x + i][y + j] == 0 and\
                explosionsMap[x + i][y + j] - NrEpisodStepsInTheFuture <= 0:
                futureExplosionActive = [timer - NrEpisodStepsInTheFuture for (x_a, y_a, timer) in futureExplosionList
                                   if (x_a, y_a) == (x+i, y+j) and (timer - NrEpisodStepsInTheFuture in [-2, -0])]
                otherPlayersAtPosition = [(x+i, y+j) for (_, __, ___, other_Player) in otherPlayers
                                          if other_Player == (x+i, y+j)]
                isBomb = isBombAt(bombs_xy, x + i, y + j)

                #must revisit this!!!
                #this should be true only for NrEpisodStepsInTheFuture==0
                #for NrEpisodStepsInTheFuture > 0, some probability must w.r.t. otherPlayer position be involved
                if len(futureExplosionActive) == 0 and len(otherPlayersAtPosition) == 0 and not isBomb:
                    legalNextPositions.append((i, j))

    for position in legalNextPositions:
        legalActions.append(directions[position])

    # if bomb available
    # MUST INTRODUCE SOME PROBABILITY W.R.T. POSSIBLE SAFE PATH AFTER USING THE BOMB!!!!!
    #!!!!!!!!!
    if bombActionPossible:
        legalActions.append('BOMB')

    return legalActions



#DON'T use it!!!!
def getLegalActionsForPosition(position, game_state: dict):

    assert not "DON'T use it!!!!"

    legalActions = []

    legalNextPositions = []

    # user state
    (name, currentScore, bombActionPossible, (x, y)) = game_state["self"]

    #overwritten (x, y) with "position" !!!!!!
    #same algorithm now!!!!
    (x, y) = (position[0], position[1])

    # accesible game board elements
    field = game_state["field"]
    (boardSizeX, boardSizeY) = field.shape

    # bombs positons
    #bombs = game_state["bombs"]

    # exploding bombs
    #explosion_map = game_state["explosion_map"]

    # inside map && #feasible position(no stone/crates) && BombExplosionFreePosition
    for (i, j) in directionsAsList:
        if x + i in range(0, boardSizeX + 1) and y + j in range(0, boardSizeY + 1) and \
                field[x + i][y + j] == 0: # and not isBombAt(bombs, x + i, y + j):
            # self.BombExplosionFreePosition(x+i, y+j, bombs, explosion_map, field):
            legalNextPositions.append((i, j))

    for position in legalNextPositions:
        legalActions.append(directions[position])

    # if next bomb available and there is safe direction to move
    if bombActionPossible:  # and self.SafeToDropBombAtPosition(x, y, bombs, explosion_map, field):
        legalActions.append('BOMB')

    return legalActions


def getLegalActionsForAgent(game_state: dict):
    legalActions = []

    legalNextPositions = []

    # user state
    (name, currentScore, bombActionPossible, (x, y)) = game_state["self"]

    # accesible game board elements
    field = game_state["field"]
    (boardSizeX, boardSizeY) = field.shape

    # bombs positons
    bombs = game_state["bombs"]

    # exploding bombs
    explosion_map = game_state["explosion_map"]

    # inside map && #feasible position(no stone/crates)
    for (i, j) in directionsAsList:
        if x + i in range(0, boardSizeX + 1) and y + j in range(0, boardSizeY + 1) and \
                field[x + i][y + j] == 0:
            legalNextPositions.append((i, j))

    for position in legalNextPositions:
        legalActions.append(directions[position])

    # if next bomb available and there is safe direction to move
    if bombActionPossible:
        legalActions.append('BOMB')

    return legalActions

#the "legalActions" can contain "BOMB"/"WAIT" since will not be taken in consideration!!!!
def getLegalNeighborsForPosition(position, legalActions):

    (AgentPositionX, AgentPositionY) = position

    legalNeighbors = []

    AgentPosAfterAction = {
        #'BOMB': (AgentPositionX, AgentPositionY),
        #'WAIT': (AgentPositionX, AgentPositionY),
        'UP': (AgentPositionX, AgentPositionY - 1),
        'DOWN': (AgentPositionX, AgentPositionY + 1),
        'LEFT': (AgentPositionX - 1, AgentPositionY),
        'RIGHT': (AgentPositionX + 1, AgentPositionY),
    }

    for action in legalActions:
        if action != 'BOMB' and action != 'WAIT':
            legalNeighbors.append(AgentPosAfterAction[action])

    return legalNeighbors

#the "legalActions" can contain "BOMB"/ since will not be taken in consideration!!!!
def getLegalNeighborsForPositionCureentPositionIncluded(position, legalActions):

    (AgentPositionX, AgentPositionY) = position

    legalNeighbors = []

    AgentPosAfterAction = {
        #'BOMB': (AgentPositionX, AgentPositionY),
        'WAIT': (AgentPositionX, AgentPositionY),
        'UP': (AgentPositionX, AgentPositionY - 1),
        'DOWN': (AgentPositionX, AgentPositionY + 1),
        'LEFT': (AgentPositionX - 1, AgentPositionY),
        'RIGHT': (AgentPositionX + 1, AgentPositionY),
    }

    for action in legalActions:
        if action != 'BOMB':
            legalNeighbors.append(AgentPosAfterAction[action])

    return legalNeighbors

def getLegalNextPositionsAfterLegalActions(position, legalActions):

    (AgentPositionX, AgentPositionY) = position

    legalNextPositions = []

    AgentPosAfterAction = {
        'BOMB': (AgentPositionX, AgentPositionY),
        'WAIT': (AgentPositionX, AgentPositionY),
        'UP': (AgentPositionX, AgentPositionY - 1),
        'DOWN': (AgentPositionX, AgentPositionY + 1),
        'LEFT': (AgentPositionX - 1, AgentPositionY),
        'RIGHT': (AgentPositionX + 1, AgentPositionY),
    }

    for action in legalActions:
        legalNextPositions.append(AgentPosAfterAction[action])

    return legalNextPositions

#the "legalActions" can contain "BOMB"/"WAIT" since will not be taken in consideration!!!!
def getLegalNeighborsFor(state: dict, legalActions):

    # user state
    (name, currentScore, bombActionPossible, (AgentPositionX, AgentPositionY)) = state["self"]

    legalNeighbors = []

    AgentPosAfterAction = {
        #'BOMB': (AgentPositionX, AgentPositionY),
        #'WAIT': (AgentPositionX, AgentPositionY),
        'UP': (AgentPositionX, AgentPositionY - 1),
        'DOWN': (AgentPositionX, AgentPositionY + 1),
        'LEFT': (AgentPositionX - 1, AgentPositionY),
        'RIGHT': (AgentPositionX + 1, AgentPositionY),
    }

    for action in legalActions:
        if action != 'BOMB' and action != 'WAIT':
            legalNeighbors.append(AgentPosAfterAction[action])

    return legalNeighbors