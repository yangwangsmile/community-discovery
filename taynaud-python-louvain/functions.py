import community as c
import networkx as nx
import pickle
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np
import pandas as pd

#Functions for loading/saving objects
def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

#Community functions
''' Return list of tuples with the communities and its number of members
    sorted by number of members'''
def ranking_members_community (partition,from_below=False):
    countCommunities = []
    for com in set(partition.values()):
        count = sum( x == com for x in partition.values())
        countCommunities.append([com,count])
    ranking = sorted(countCommunities, key=lambda tup: tup[1],reverse= not from_below)
    return ranking

''' Return induced graph of top N communities with more members'''
def induced_graph_ranking(G,partition,ranking,topN):
    [subG,reduced_partition] = subgraph_ranking((G,partition,ranking,topN))
    ind = c.induced_graph(reduced_partition, subG)
    return ind

''' Return sub graph and reduced partition of top N communities with more members'''
def subgraph_ranking(G,partition,ranking,topN):
    communities = [x[0] for x in ranking[0:topN]]
    reduced_partition =  { k:v for k, v in partition.items() if v in communities}
    nodes = reduced_partition.keys()
    subG = G.subgraph(nodes)
    return [subG,reduced_partition]


''' Return sub graph of a certain community'''
def subgraph_community(G,partition,community):
    nodes = list((k) for k,v in partition.items() if v == community)
    subG = G.subgraph(nodes)
    return subG

def read_communities():
    with open('communities_new.txt',encoding='latin-1') as file:
        for line in file:
            community = set()
            for word in line.split():
                if word.isnumeric():
                    community.add(word)
            yield community

def same_community(communities, u, v):
    for community in communities:
        if u in community and v in community:
            return True
    return False

def read_ground_truth():
    df = pd.read_csv("author_label.txt",encoding="latin-1") 
    return df

''' Calculate purity from a group of communities and a ground_truth'''
def purity(clusters,ground_truth,communityAPI=False):
    
    if communityAPI:
        partition = []
        for communities in set(clusters.values()):
            partition.append([])
        for k,v in clusters.items():
            partition[v].append(k)
        clusters =  partition
    confusion_matrix = np.zeros((len(clusters),6))
    for idx,cluster in enumerate(clusters):
        for node in cluster:
            #Find real cluster in ground truth
            node_gt = ground_truth.ix[int(node)]
            for i in range(0,6):
                confusion_matrix [idx,i] += node_gt[' label' + str(i)]
    return sum(np.amax(confusion_matrix,axis=1))/sum(sum(confusion_matrix))


##Role functions

''' Return role score for node n in graph G'''
def diverse_actor(G, n):
    subgraph = G.subgraph(G.neighbors(n))
    num_components = 0
    for component in nx.connected_components(subgraph):
        if len(component) >= 3:
            num_components+=1
    return num_components

''' Return list of tuples with the top N opinion leaders and their score'''
def opinion_leaders (G,topN):
    scores = nx.pagerank(G)
    ranking = sorted(scores, key=scores.get,reverse=True)
    if (topN > len(scores)): topN = len(scores)
    topRanking=[]
    for i in range(0,topN):
        topRanking.append([ranking[i],scores[str(ranking[i])]])
    return topRanking

def community_core(G, n, triangles = None):
    if triangles is None:
        triangles = sum(nx.triangles(G).values())/3
    return nx.triangles(G, n)/triangles

#Display functions
def display_partition (G,partition,figureNumber=1,edgeWidth=1,nodeSize=10):

    size = float(len(set(partition.values())))

    #Define colors of the clusters
    norm = colors.Normalize(vmin=0, vmax=size, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.rainbow)

    #Display partition
    plt.figure(figureNumber)
    pos = nx.random_layout(G)
    count = 0
    for com in set(partition.values()) :
        count = count + 1.
        list_nodes = [nodes for nodes in partition.keys()
                                    if partition[nodes] == com]
        nx.draw_networkx_nodes(G, pos, list_nodes, node_size = nodeSize,
                                    node_color = mapper.to_rgba(count))
    nx.draw_networkx_edges(G,pos, alpha=0.2, width=edgeWidth)
    plt.show()
