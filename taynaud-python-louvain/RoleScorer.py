import networkx as nx
import numpy as np
import functions as fx
from enum import Enum

class RoleScorer:

    def __init__(self, G):
        self.G = G
        self.pagerank = None
        self.triangles = None
        self.node_communities = None
        self.Roles = Enum("Role", "structural_hole diverse_actor community_bridge opinion_leader community_core")
        self.p = None
        self.q = None

    def structural_hole(self, n):
        if self.node_communities is None:
            self.node_communities = dict()
            communities = list(fx.read_communities())
            for node in nx.nodes_iter(self.G):
                self.node_communities[node] = 0
            for community in communities:
                for node in community:
                    if node in self.node_communities.keys():
                        self.node_communities[node] += 1
                    else:
                        self.node_communities[node] = 0
        return self.node_communities[n]

    def diverse_actor(self, n):
        subgraph = self.G.subgraph(self.G.neighbors(n))
        num_components = 0
        for component in nx.connected_components(subgraph):
            if len(component) >= 3:
                num_components+=1
        return num_components

    def community_bridge(self, n):
        N = set(self.G.neighbors(n))
        communities = list(fx.read_communities())
        if self.p is None:
            complete = 0
            for pair in nx.edges_iter(self.G):
                if fx.same_community(communities, pair[0], pair[1]):
                    #Pair is complete
                    complete += 1
            #Probability two linked nodes belong to same community
            self.p = complete / nx.number_of_edges(self.G)
            print("p =", self.p)

        if self.q is None:
            pure = 0
            nonlinked = 0
            for pair in nx.non_edges(self.G):
                nonlinked += 1
                if not fx.same_community(communities, pair[0], pair[1]):
                    #Pair is pure
                    pure += 1
            #Probability two non-linked nodes do not belong to same comunity
            self.q = pure/nonlinked
            print("q =", self.q)

        sum = 0
        for vj in N:
            #Number of common neighbors
            n1 = len(N.intersection(set(self.G.neighbors(vj))))
            n2 = len(N)-n1
            sum += 1/(1+n1*self.p +n2*(1-self.q))
        return sum

    def opinion_leader(self, n):
        if self.pagerank is None:
            self.pagerank = nx.pagerank(self.G)
        return self.pagerank[n]

    def community_core(self, n):
        if self.triangles is None:
            self.triangles = sum(nx.triangles(self.G).values())/3
        return nx.triangles(self.G, n)/self.triangles

    def getRoleScore(self, n, role):
        if role == self.Roles.structural_hole:
            return self.structural_hole(n)
        elif role == self.Roles.diverse_actor:
            return self.diverse_actor(n)
        elif role == self.Roles.community_bridge:
            return self.community_bridge(n)
        elif role == self.Roles.opinion_leader:
            return self.opinion_leader(n)
        elif role == self.Roles.community_core:
            return self.community_core(n)
        else:
            raise Exception()

    def getScores(self, n):
        return {
            self.Roles.structural_hole: self.structural_hole(n),
            self.Roles.diverse_actor: self.diverse_actor(n),
            self.Roles.community_bridge: self.community_bridge(n),
            self.Roles.opinion_leader: self.opinion_leader(n),
            self.Roles.community_core: self.community_core(n),
        }

    def getTopXScores(self, role, topX):
        scores = []
        for node in nx.nodes_iter(self.G):
            scores.append((node, self.getRoleScore(node, role)))
        # Sort by score:
        scores = sorted(scores, reverse=True, key=lambda tup : tup[1])
        return scores[0:topX]

    def getRoleCounts(self):
        roleranks = dict()
        for role in self.Roles:
            scores = []
            for node in nx.nodes_iter(self.G):
                scores.append(self.getRoleScore(node, role))

            #Calculate ranks of scores (I don't understand this part either)
            u, v = np.unique(scores, return_inverse=True)
            ranks = (np.cumsum(np.concatenate(([0], np.bincount(v)))))[v]

            roleranks[role] = ranks

        rolenums = dict()
        for role in self.Roles:
            rolenums[role] = 0
        rolenums[None] = 0
        # Get highest ranked role for each node
        for node in range(nx.number_of_nodes(self.G)):
            highest_role = None
            max_rank = 0
            for role in self.Roles:
                if roleranks[role][node] > max_rank:
                    max_rank = roleranks[role][node]
                    highest_role = role
            print(highest_role)
            rolenums[highest_role] += 1
        return rolenums
