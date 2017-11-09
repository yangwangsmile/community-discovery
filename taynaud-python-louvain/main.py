import community
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import functions as fx

############## CONFIGURATION ##############
dataset = 2
load_partition=True
display_plots=False
###########################################

#Load sample social network
if dataset == 1:
    G = nx.read_edgelist('DBLP_graph.txt')
elif dataset == 2:
    G = nx.read_edgelist('soc-flickr.mtx')
else:
    print('A valid dataset number was not provided')
    exit()

#Print information of dataset
print ('Number of nodes: ', nx.number_of_nodes(G))
print ('Number of edges: ', nx.number_of_edges(G))

#Example datasets
#G = nx.karate_club_graph()
#G = nx.davis_southern_women_graph()
#G = nx.florentine_families_graph()

if display_plots:
    #Configure layout
    pos = nx.random_layout(G)

    #Display original graph
    plt.figure(1)
    nx.draw_networkx_edges(G,pos, alpha=0.5)
    nx.draw_networkx_nodes(G, pos,node_size=10,node_color='1')

    plt.show()

if load_partition:
    #Load partition from file
    partition = fx.load_obj('partition_dataset_' + str(dataset))
    size = float(len(set(partition.values())))
else:
    #Compute the best partition
    partition = community.best_partition(G)
    size = float(len(set(partition.values())))
    print('Number of communities: {0}'.format(int(size)))

    #Save partition in file
    fx.save_obj(partition, 'partition_dataset_' + str(dataset))

#Clustering evaluation
print('Modularity: {0:.4f}'.format(community.modularity(partition,G)))

if display_plots:
    fx.display_partition(G,partition,2)

#Calculate induced graph
#ind = community.induced_graph(partition, G)

#Display induced graph
#if display_plots:
#   plt.figure(3)
#   pos = nx.random_layout(ind)
#   nx.draw_networkx_edges(ind,pos, alpha=0.5)
#   nx.draw_networkx_nodes(ind, pos,node_size=40,node_color='1')
#   plt.show()

#Get Opinion Leaders(OP)
print(fx.opinion_leaders(G,20))
