# Evolution of Cooperation

This project investigates how cooperation can evolve in agent-based models. 

## Simulations
The diagram below broadly illustrates the flow of all evolution simulations. Each generation has a fixed population size and each generation's agents are descendents of the previous generation.

![simulation_diagram](https://github.com/philipp-hellwig/evolution-language-simulation/assets/108931950/62039580-c824-416f-9a1b-b004e3bbfdfe)

### Inheritance & Traits
Each agent has a DNA sequence that determines their probability to communicate and to do so maliciously or not. Triplets of the DNA sequence are randomly inherited either from the father (F) or mother (M) where each nucleotide has a chance to mutate ($\mu=0.01$).

![image](https://github.com/philipp-hellwig/evolution-language-simulation/assets/108931950/0a1e6d4d-edd4-4833-8cf3-317164e23138)

### Interactions
During the lifetime of a generation, agents are repeatedly presented with food opportunities. Agents can choose three different options:

![image](https://github.com/philipp-hellwig/evolution-language-simulation/assets/108931950/9957aea1-e333-4d8d-9c61-74a73f50b10f)

After each iteration, the food agents acquired decays. If an agent drops below 0 food during the simulation, they die and thus cannot reproduce.
