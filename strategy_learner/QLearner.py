"""
Vinay Srinath - vsrinath6
"""

import numpy as np


class QLearner(object):
    def author(self):
        return 'vsrinath6'  # replace tb34 with your Georgia Tech username.

    def __init__(self, \
                 num_states=100, \
                 num_actions=4, \
                 alpha=0.2, \
                 gamma=0.9, \
                 rar=0.5, \
                 radr=0.99, \
                 dyna=0, \
                 verbose=False):

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
        self.s_experienced = []
        self.a_experienced = []
        self.s_prime_experienced = []
        self.r_experienced = []
        self.QTable = np.zeros((self.num_states, self.num_actions))

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        self.s = s
        # action = rand.randint(0, self.num_actions-1)
        action = np.argmax(self.QTable[s, :])
        if self.verbose: print "s =", s, "a =", action
        return action

    def query(self, s_prime, r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        ## Update rule
        self.QTable[self.s, self.a] = (1 - self.alpha) * self.QTable[self.s, self.a] + self.alpha * (
            r + (self.gamma * np.max(self.QTable[s_prime, :])))
        self.s_experienced.append(self.s)
        self.s_prime_experienced.append(s_prime)
        self.a_experienced.append(self.a)
        self.r_experienced.append(r)

        ## Hallucinate
        if self.dyna > 0:
            iterations = min(self.dyna, len(self.s_experienced))
            for i in range(iterations):
                n = np.random.randint(0, len(self.s_experienced))
                self.QTable[self.s_experienced[n], self.a_experienced[n]] = (1 - self.alpha) * self.QTable[
                    self.s_experienced[n], self.a_experienced[n]] + self.alpha * (
                    self.r_experienced[n] + self.gamma * np.max(self.QTable[self.s_prime_experienced[n], :]))

        ## Remember state and return action
        self.s = s_prime
        if np.random.uniform(0.0, 1.0) > self.rar:
            action = np.argmax(self.QTable[s_prime, :])
        else:
            action = np.random.randint(self.num_actions)
        self.rar *= self.radr
        self.a = action
        if self.verbose: print "s =", s_prime, "a =", action, "r =", r
        return action


if __name__ == "__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
