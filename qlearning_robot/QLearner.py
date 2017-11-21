"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):

    def author(self):
        return 'vsrinath6'  # replace tb34 with your Georgia Tech username.

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.num_actions = num_actions
        self.s = 0
        self.a = 0
        self.num_states = num_states
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna

        self.QTable = np.zeros((self.num_states,self.num_actions))
        if self.dyna > 0:
            self.Tc = np.ones((self.num_states,self.num_actions,self.num_states)) * 0.00001
            self.T = self.Tc / self.Tc.sum(axis=2,keepdims=True)
            self.R = -1.0 * np.ones((self.num_states,self.num_actions))


    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        #action = rand.randint(0, self.num_actions-1)
        action = np.argmax(self.QTable[s,:])
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        ## Update rule
        self.QTable[self.s,self.a] = (1-self.alpha) * self.QTable[self.s,self.a] + self.alpha * (r + (self.gamma * np.max(self.QTable[s_prime,:])))

        if self.dyna > 0:
            self.Tc[self.s,self.a,s_prime] += 1

            self.T[self.s,self.a,:] = self.Tc[self.s,self.a,:]/self.Tc[self.s,self.a,:].sum()

            self.R[self.s,self.a] = (1-self.alpha) * self.R[self.s,self.a] + self.alpha * r

            s_samples = np.random.randint(0, self.num_states, self.dyna)
            a_samples = np.random.randint(0, self.num_actions, self.dyna)

            # For each sample...
            for i in range(self.dyna):
                s = s_samples[i]
                a = a_samples[i]
                # Simulate an action with the transition model and land on an s_prime
                s_prime = np.argmax(np.random.multinomial(1, self.T[s, a, :]))
                # Compute reward of simulated action.
                r = self.R[s, a]
                # Update Q
                self.QTable[s, a] = (1 - self.alpha) * self.QTable[s, a] + self.alpha * (r + self.gamma * np.max(self.QTable[s_prime, :]))

        if rand.random() > self.rar:
            action = np.argmax(self.QTable[s_prime, :])
        else:
            action = rand.randrange(self.num_actions)

        # Decay rar.
        self.rar *= self.radr

        self.s = s_prime
        self.a = action
        if self.verbose: print "s =", s_prime,"a =",action,"r =",r
        return action

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
