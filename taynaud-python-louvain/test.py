import RoleScorer as rs
import networkx as nx
#Load sample social network
G = nx.read_edgelist('com-dblp.ungraph.txt',nodetype=str)
for e in G.edges():
    print (e)
    break
roleScorer = rs.RoleScorer(G)
result = roleScorer.getScores('269039')
print(result)
# roleScorer.getRoleCounts()