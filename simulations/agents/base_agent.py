import numpy as np
import warnings
from itertools import chain
import scipy.stats as st
import random

class Agent():
    nucleotides = ["a","t","c","g"]
    food_individual_consumption = 1.6
    food_sharing = 1.5
    food_stealing = 3
    food_decay = 1.75

    # used to adjust class variables above
    @classmethod
    def set_class_variables(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                warnings.warn(f"Class has no attribute '{key}'")

    def __init__(self, mu: float, parents=None):
        self.parents = parents
        self.dna = np.random.choice(Agent.nucleotides, 90) if parents is None else self.inherit(parents, mu)
        self.malintent, self.communication = self.features_from_dna(self.dna)
        self.prob_malintent = self.malintent/(len(self.dna)/6)
        self.prob_communication = self.communication/(len(self.dna)/6)
        self.food_counter = 5 # initial amount of food reserves an individual is born with
        self.reputation = 1


    # inheritance method
    def inherit(self, parents: tuple, mu: float):
        # inheritance:
        child_dna = []
        for i in range(0, (len(parents[0].dna)-2), 3):
            child_dna.append(list(np.random.choice(parents).dna[i:i+3]))
        # random mutation:
        child_dna = list(chain(*child_dna))
        for i in range(len(child_dna)):
            if st.bernoulli(mu).rvs(1):
                child_dna[i] = random.choice(Agent.nucleotides)
        return child_dna

    # extract features from DNA
    def features_from_dna(self, dna: list):
        communication, malintent = 0, 0
        for i in range(0, len(dna), 3):
            if i < (len(dna)/2):
                # every occurrence of "c,c,t" counts as +1 to malintent feature
                if "".join(dna[i:i+3])=="cct":
                    communication += 1
            else:
                # every occurrence of "g,a,t" counts as +1 to communication feature
                if "".join(dna[i:i+3])=="gat":
                    malintent += 1
        return (malintent, communication)

    # food opportunity interaction:
    def found_food(self, other):
        # decide to communicate or not:
        if st.bernoulli(self.prob_communication).rvs(1):
            # other also has to be willing to communicate
            if st.bernoulli(other.prob_communication).rvs(1):
                # decide to try to steal food or not
                if st.bernoulli(self.prob_malintent).rvs(1):
                    # other has good intentions:
                    if not st.bernoulli(other.prob_malintent).rvs(1):
                        self.food_counter += Agent.food_stealing
                    # other also wants to steal the food:
                    else:
                        np.random.choice([self, other]).food_counter += Agent.food_stealing
                else:
                    if st.bernoulli(other.prob_malintent).rvs(1):
                        other.food_counter += Agent.food_stealing
                    else:
                        # share food:
                        self.food_counter += Agent.food_sharing
                        other.food_counter += Agent.food_sharing
                        # increase reputation:
                        self.reputation += 1
                        other.reputation += 1
            else:
                self.food_counter += Agent.food_individual_consumption
        else:
            self.food_counter += Agent.food_individual_consumption


    def starve(self):
        starved = self.food_counter < 0
        return starved

    def apply_food_decay(self):
        self.food_counter -= Agent.food_decay

    def __str__(self):
        return(
            f"Agent (Parents: {self.parents})\n"
            "##### Features #####\n"
            f"Communication: {self.communication}\n"
            f"Malintent: {self.malintent}\n"
            f"Reputation: {self.reputation}\n"
        )