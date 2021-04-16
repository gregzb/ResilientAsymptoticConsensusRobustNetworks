import networkx as nx
import matplotlib.pyplot as plt
import random
import statistics

import utils

def simulate_time_step(graph):
    graph_copy = utils.copy_graph(graph)

    F = graph.graph['F']

    for node in graph_copy:
        values = [(graph.nodes[node]['value'], True)]
        for u, v in graph_copy.in_edges(node):
            values.append((graph.nodes[u]['value'], False))
        values.sort()

        original_idx = [v[1] for v in values].index(True)

        filtered_values = [v[0] for i,v in enumerate(values) if i >= min(F, original_idx) and i < max(original_idx+1, len(values) - F)]

        weights = [1/len(filtered_values) for _ in range(len(filtered_values))]

        graph_copy.nodes[node]['value'] = utils.dot(weights, filtered_values)
    return graph_copy

def apply_malicious_values(graph, f):
    graph_copy = utils.copy_graph(graph)

    for node in graph_copy.nodes():
        malicious = graph_copy.nodes[node]['malicious']
        if malicious:
            graph_copy.nodes[node]['value'] = f(node)

    return graph_copy

def good_node_stats(graph):
    values = []
    for node in graph.nodes():
        malicious = graph.nodes[node]['malicious']
        if not malicious:
            values.append(graph.nodes[node]['value'])
    return statistics.mean(values), statistics.variance(values)

def plot_simulation_data(graph, node_history, variance_history):
    figure, axis = plt.subplots(2)

    dict_value = next(iter(node_history.values()))
    indices = [i for i in range(len(dict_value))]
    for node in graph.nodes():
        col = 'red' if graph.nodes[node]['malicious'] else 'blue'
        axis[0].plot(indices, node_history[node], color = col)
    
    # red is malicious, blue is normal
    axis[0].set_title('Values Over Time')

    indices = [i for i in range(len(variance_history))]
    axis[1].plot(indices, variance_history, color = 'blue') # all variances are blue
    axis[1].plot(indices, [0 for _ in indices], color = 'green') # 0 baseline is green

    axis[1].set_title('Variance (of "Good" Nodes) Over Time')

    plt.show()

def main():

    SEED = 6
    TIME_STEPS = 100
    DELTA_VARIANCE_EPSILON = pow(10,-12)

    random.seed(SEED)

    # ceil(7/2) = 4, defends against up to 3
    # (ceil(n/2), n)-robust
    # defends against (ceil(n/2)-1) malicious total
    graph = nx.complete_graph(101, nx.DiGraph())
    graph.graph['F'] = 50

    for node in graph.nodes():
        graph.nodes[node]['malicious'] = False

    malicious_nodes = random.choices(graph.nodes(), k=graph.graph['F'])
    for node in malicious_nodes:
        node['malicious'] = True

    target_value = 1000
    std_dev = 1

    for node in graph.nodes():
        if not graph.nodes[node]['malicious']:
            graph.nodes[node]['value'] = random.gauss(target_value, std_dev)

    MAL_target_value = 1010
    MAL_std_dev = 2

    malicious_function = lambda node: random.gauss(MAL_target_value, MAL_std_dev)

    graph = apply_malicious_values(graph, malicious_function)

    print("Initial State: ")
    for node in graph.nodes():
        print(node, graph.nodes[node])

    print(f"Initial Good (mean, variance): {good_node_stats(graph)}")

    print("~"*80)

    indices = [0]
    node_values = {}
    for node in graph.nodes():
        node_values[node] = [graph.nodes[node]['value']]

    variance_history = [good_node_stats(graph)[1]]

    curr_graph = graph
    for iteration in range(1, TIME_STEPS+1):
        curr_graph = apply_malicious_values(simulate_time_step(curr_graph), malicious_function)

        new_mean, new_variance = good_node_stats(curr_graph)

        print(f"Iteration {iteration}: {(new_mean, new_variance)}")

        indices.append(iteration)
        for node in curr_graph.nodes():
            node_values[node].append(curr_graph.nodes[node]['value'])

        variance_history.append(new_variance)

        if iteration >= 2:
            variance_change = abs(variance_history[iteration] - variance_history[iteration-2])
            if variance_change < DELTA_VARIANCE_EPSILON:
                print(f"Stopped after iteration {iteration} because the change in variance was small.")
                break

    print(f"Final Good (mean, variance): {good_node_stats(curr_graph)}")

    plot_simulation_data(curr_graph, node_values, variance_history)


if __name__ == '__main__':
    main()