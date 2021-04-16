import networkx as nx
import copy

# file format is:
# [num verts] [num malicious] [num edges]
# [num verts]-[num malicious] lines of [vert number] [value]
# [num malicious] lines of [vert number] [malicious value]
# [num edges] of lines of [from node] [to node]

# all nodes expected to be 0 to [num verts]-1
def load_graph(file_name):
    tmp_graph = nx.DiGraph()
    with open(file_name, 'r') as f:
        n, m, e, F = map(int, f.readline().strip().split())
        tmp_graph.graph['F']=F
        tmp_graph.add_nodes_from([i for i in range(n)])
        for _ in range(n-m):
            node, value = f.readline().strip().split()
            node = int(node)
            value = float(value)
            tmp_graph.nodes[node]['value'] = value
            tmp_graph.nodes[node]['malicious'] = False
        for _ in range(m):
            node, value = f.readline().strip().split()
            node = int(node)
            value = float(value)
            tmp_graph.nodes[node]['value'] = value
            tmp_graph.nodes[node]['malicious'] = True
        for _ in range(e):
            u, v = map(int, f.readline().strip().split())
            tmp_graph.add_edge(u,v)

    return tmp_graph

def dot(l1, l2):
    return sum([a*b for a,b in zip(l1, l2)])

def copy_graph(graph):
    # graph_copy = graph.__class__()
    # graph_copy.add_nodes_from(graph)
    # graph_copy.add_edges_from(graph.edges)

    # for node in graph_copy.nodes():
    #     for prop in graph.nodes[node]:
    #         graph_copy.nodes[node][prop] = graph.nodes[node][prop]

    # return graph_copy
    return copy.deepcopy(graph)