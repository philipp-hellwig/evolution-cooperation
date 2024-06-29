import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from agents.bayesian_agent import BayesianAgent


def plot_simulation_stats(simulation_stats, starvation_plot=False, intruders=[]):
    """
    simulation_stats: a data frame with columns "generation", "probability", "trait", "starvation"
    return: a lineplot plotting 
    """
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))
    _ = sns.lineplot(data=simulation_stats.loc[:, simulation_stats.columns!="starvation"], x="generation", y="probability", hue="trait", errorbar=("se", 1), ax=ax[0])
    _ = ax[0].set_ylim(0,1)
    _ = ax[0].vlines(intruders[1:], ymin=0, ymax=17, colors="black", linestyles="dotted")

    if starvation_plot:
        s_df = simulation_stats[simulation_stats["starvation"].notnull()]
        _ = ax[1].scatter(s_df["generation"], s_df["starvation"])
        _ = ax[1].set_ylim(0,30)
        _ = ax[1].set_xlabel("generation")
        _ = ax[1].set_ylabel("starvation")
        _ = ax[1].vlines(intruders[1:], ymin=0, ymax=30, colors="black", linestyles="dotted")
        _ = ax[1].legend(["starvation", "free riders"])
        plt.show()
    else:
        plt.show()
    return fig

def plot_averaged_simulations(simulations: list[pd.DataFrame]):
    concatenated = pd.concat(simulations)
    _ = sns.lineplot(data=concatenated, x="generation", y="probability", hue="trait", errorbar=("se", 1))
    _ = plt.ylim(0,1)
    plt.show()

def plot_learned_distribution_matrix(gens: dict, figsize=(18,4), intruder=False):
    fig, ax = plt.subplots(1, len(gens.keys())-1 , figsize=figsize)
    for i, generation in enumerate(gens.items()):
        if i>0:
            gen, agents = generation
            comm_matrix = pd.DataFrame(columns=[str(agent.id) for agent in agents])
            for agent in agents:
                for other in agents:
                    comm_matrix.loc[agent.id, str(other.id)] = agent.beta_communicate[other][0]/sum(agent.beta_communicate[other]) if agent is not other else 0.
            comm_matrix = comm_matrix.apply(pd.to_numeric, errors='coerce')
            _ = sns.heatmap(comm_matrix, cmap="viridis", vmin=0, vmax=1, ax=ax[i-1], cbar_kws={'label': 'P(communicate|agent)'})
            _ = ax[i-1].set_title(f"Learned Dists after {gen} Generations")
            _ = ax[i-1].set_xlabel("agent ids")
            _ = ax[i-1].set_ylabel("agent ids")
    plt.show()
    return fig

def plot_communication_network(gen: list[BayesianAgent]):
    G = nx.Graph()
    colormap = []
    for agent in gen:
        G.add_node(agent)
        colormap.append("red" if "intruder" in str(agent.id) else "black")
    pos = nx.spring_layout(G)
    nx.layout
    nx.draw_networkx_nodes(G, pos, node_color=colormap, node_size=75)
    for agent in gen:
        for other in gen:
            if agent is not other:
                weight = agent.beta_communicate[other][0]-agent.communication + agent.beta_communicate[other][1]-(len(agent.dna)/6-agent.communication)
                if weight > 0:
                    G.add_edge(agent, other, weight=weight)
    all_weights = []
    for (node1,node2,data) in G.edges(data=True):
        all_weights.append(data['weight'])
    unique_weights = list(set(all_weights))
    for weight in unique_weights:
        weighted_edges = [(node1,node2) for (node1,node2,edge_attr) in G.edges(data=True) if edge_attr['weight']==weight]
        width = weight*len(gen)*3/sum(all_weights)
        nx.draw_networkx_edges(G,pos,edgelist=weighted_edges,width=width)
    plt.show()

