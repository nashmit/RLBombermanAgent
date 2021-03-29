import numpy as np

from random import Random

from .FeatureExtractor import *
from .vector import *

from .Actions import *

import traceback

class ApproximateQAgent():

    # epsilon MUST BE 0 for using the agent and non zero for learning mode
    # another element MUST BE 0 for nonlerning mode
    def __init__(self, extractor, epsilon=0.02, alpha=0.05, gamma=0.90): #epsilon=0.05 alpha=0.02
        self.epsilon = epsilon
        self.alpha = alpha
        self.discount = gamma

        self.featExtractor = extractor

        self.weights = ones(extractor.getNumberOf())  #must do this size independent!!!!
        self.randGenerator = Random()

        self.directions = {
            (-1, 0): 'LEFT',
            (0, 0): 'WAIT',
            (1, 0): 'RIGHT',
            (0, -1): 'UP',
            (0, 1): 'DOWN'
        }

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):

        #return self.getWeights() * self.featExtractor(state, action)
        return dot(self.getWeights(), self.featExtractor.getFeatures(state, action))

    def update(self, state, action, nextState, reward):

        gain = (reward + self.discount * self.calculateValueFromQValues(nextState)) - self.getQValue(state, action)

        # print("reward: ", reward,
        #       "discount: ", self.discount,
        #       "computeValueFromQValues(nextState): ", self.computeValueFromQValues(nextState),
        #       "self.getQValue(state, action): ", self.getQValue(state, action))

        features = self.featExtractor.getFeatures(state, action)

        for i in range(0, features.size()):
            # print("i: ", i,
            #       "weights[i]: ", self.weights[i],
            #       "self.alpha: ", self.alpha,
            #       "gain: ", gain,
            #       "features[i]: ", features[i])
            self.weights[i] += self.alpha * gain * features[i]
        #print(" ")

    def calculateValueFromQValues(self, state):

        if len(getLegalActionsForAgent(state)) == 0:
            return 0.0
        value = float('-inf')

        #print("calculateValueFromQValues: ")
        for action in getLegalActionsForAgent(state):
            value = max(value, self.getQValue(state, action))
            #print("step: ", state["step"], " action:", action, "value: ", value)
        return value

    def myRand(self, eps):
        r = self.randGenerator.random()
        return r < eps


    def getAction(self, state):

        legalActions = getLegalActionsForAgent(state)
        action = None

        self.featExtractor.ComputeAndNormalizeFeaturesForAllLegalActionsFor(state)

        if self.epsilon != 0 and self.myRand(self.epsilon):
            action = self.randGenerator.choice(legalActions)
        else:
            action = self.getPolicy(state)

        if action is None:
            action = 'WAIT'

        # #agent
        # (
        #     AgentName,
        #     currentScore,
        #     bombsAvailable,
        #     (AgentPositionX, AgentPositionY)
        # ) = state['self']
        # #stepCurrentEpisod
        # stepCurrentEpisod = state['step']
        #
        # print("stepCurrentEpisod: ", stepCurrentEpisod, "action: ", action)

        #print("Current Step Weights: ", self.getWeights())
        #print("Decided for action: ", action)

        return action

    def getPolicy(self, state):
        return self.extractActionFromQValues(state)

    def setEpsilon(self, epsilon):
        self.epsilon = epsilon

    def setLearningRate(self, alpha):
        self.alpha = alpha

    def setDiscount(self, discount):
        self.discount = discount

    def extractActionFromQValues(self, state):

        actions = getLegalActionsForAgent(state)
        if len(actions) == 0:
            return None
        bestAction = []
        bestQValue = self.calculateValueFromQValues(state)
        #print("")
        for action in actions:
            QV = self.getQValue(state, action)  # extract actions with bestQvalue
            if bestQValue == QV:
                bestAction.append(action)  # in case multiple actions have the same bestQValue
            #print("action: ", action,  self.featExtractor.getFeatures(state, action), "QValue: ", QV)
        return self.randGenerator.choice(bestAction)
