import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import scipy.stats as st
from agents.base_agent import Agent

class BayesianAgent(Agent):
    id = 0
    smoothing = 0.0001

    def __init__(self, *args, **kwargs):
        super(BayesianAgent, self).__init__(*args, **kwargs)
        self.cohort = []
        self.beta_communicate = self.prior_communication
        self.beta_malintent = self.malintent
        self.last_interaction = []
        self.id = BayesianAgent.id
        self.reputation = 1
        BayesianAgent.id += 1
        
    def set_cohort(self, cohort: list):
        self.cohort = [agent for agent in cohort if agent is not self]
        smoothing = BayesianAgent.smoothing
        self.beta_communicate = {agent: [self.communication+smoothing, (len(self.dna)/6-self.communication)+smoothing] for agent in self.cohort}
        self.beta_malintent = {agent: [self.malintent+smoothing, (len(self.dna)/6-self.malintent)+smoothing] for agent in self.cohort}

    def likelihood_communicate(self, other):
        a, b = self.beta_communicate[other]
        return st.beta.rvs(a, b)
    
    def likelihood_malintent(self, other):
        a, b = self.beta_malintent[other]
        return st.beta.rvs(a, b)

    def plot_beta(self, other, feature="both"):
        """
        other: another BayesianAgent
        feature: which feature ("communicate", "malintent", or "both")
        output:
        graph of beta distribution likelihood of feature given the other BayesianAgent.
        """
        if feature == "communicate":
            x = np.linspace(0,1,200)
            a, b = self.beta_communicate[other]
            _ = plt.plot(x, st.beta.pdf(x, a, b))
            _ = plt.xlabel("theta")
            _ = plt.ylabel("density")
            return plt
        
        elif feature == "malintent":
            x = np.linspace(0,1,200)
            a, b = self.beta_communicate[other]
            _ = plt.plot(x, st.beta.pdf(x, a, b))
            _ = plt.xlabel("theta")
            _ = plt.ylabel("density")
            return plt

        else:
            theta = np.linspace(0,1,200)
            a, b = self.beta_communicate[other]
            a_mal, b_mal = self.beta_malintent[other]
            data = pd.DataFrame([(st.beta.pdf(x, a, b), st.beta.pdf(x, a_mal, b_mal)) for x in theta], index=theta, columns=["communication", "malintent"])
            _ = sns.lineplot(data=data)
            _ = plt.xlabel("theta")
            _ = plt.ylabel("density")
            return plt        
        
        
    # rewrite food opportunity interaction:
    def found_food(self, other):
        # decide to communicate or not:
        if st.bernoulli(self.likelihood_communicate(other)).rvs(1):
            # other also has to be willing to communicate
            if st.bernoulli(other.likelihood_communicate(self)).rvs(1):
                # decide to try to steal food or not
                if st.bernoulli(self.likelihood_malintent(other)).rvs(1):
                    # other has good intentions:
                    if not st.bernoulli(other.likelihood_malintent(self)).rvs(1):
                        self.win_food(other)
                        other.update_beta_malintent(self, positive_outcome=True)
                    # if other also wants to steal the food:
                    else:
                        winner = np.random.choice([self, other])
                        if winner is self:
                            self.win_food(other)
                            self.update_beta_malintent(other, positive_outcome=True)
                            other.update_beta_malintent(self, positive_outcome=False)
                        else:
                            self.lose_food(other)
                            other.update_beta_malintent(self, positive_outcome=True)
                            self.update_beta_malintent(other, positive_outcome=False)
                else:
                    if st.bernoulli(other.likelihood_malintent(self)).rvs(1):
                        self.lose_food(other)
                        other.update_beta_malintent(self, positive_outcome=True)
                    else:
                        self.share_food(other)
                        self.reputation += 1
                        other.reputation += 1
            else:
                self.food_counter += BayesianAgent.food_individual_consumption
        else:
            self.food_counter += BayesianAgent.food_individual_consumption

    def win_food(self, other):
        self.food_counter += BayesianAgent.food_stealing
        self.update_beta_communicate(other, positive_outcome=True)
        other.update_beta_communicate(self, positive_outcome=False)
        
    
    def lose_food(self, other):
        other.food_counter += BayesianAgent.food_stealing
        other.update_beta_communicate(self, positive_outcome=True)
        self.update_beta_communicate(other, positive_outcome=False)

    def share_food(self, other):
        self.food_counter += BayesianAgent.food_sharing
        other.food_counter += BayesianAgent.food_sharing
        self.update_beta_communicate(other, positive_outcome=True)
        other.update_beta_communicate(self, positive_outcome=True)

    def update_beta_communicate(self, other, positive_outcome: bool, gossip=False):
        if positive_outcome:
            self.beta_communicate[other][0] += 1
        else:
            self.beta_communicate[other][1] += 1
        if not gossip:
            self.last_interaction = [other, positive_outcome]
    
    def update_beta_malintent(self, other, positive_outcome: bool, gossip=False):
        if positive_outcome:
            self.beta_malintent[other][0] += 1
        else:
            self.beta_malintent[other][1] += 1
        if not gossip:
            self.last_interaction = [other, positive_outcome]

    def incorporate_gossip(self, sender, other, positive_outcome):
        """
        self: recipient of the gossip
        sender: agent who gossiped information to the recipient
        other: agent who the gossip is about
        positive_outcome: valence of information
        """
        if st.bernoulli(self.likelihood_communicate(sender)).rvs(1):
            self.update_beta_communicate(other, positive_outcome, gossip=True)
