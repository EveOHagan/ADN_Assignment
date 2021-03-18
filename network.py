import argparse as ap
import networkx as nx
import csv
import sys

from pip._vendor.distlib.compat import raw_input

#split horizon
SPLIT_HRZN = False

# Parse command line arguments
parser = ap.ArgumentParser(description='Simplified network in python')
parser.add_argument('-f', '--file', required=True, help='reads CSV file as input for network')
args = parser.parse_args()


# data from CSV is read in and returned
def readcsv(file):
    with open(file, 'r') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',')
        nodes_edges = []
        for line in csv_data:
            if line:  # ensures line contains data and is not empty
                if "#" not in line[0]: # if begins with '#' it is a comment
                    nodes_edges.append(line)
    return nodes_edges


# Formats edges according to the graph edge in the form: (source, destination, {'distance':3})
def format_edges(inital_edges):
    formatted_edges = []
    for edge in inital_edges:
        formatted_edges.append((edge[0], edge[1], {'distance': float(edge[2])}))
    return formatted_edges


# Routing table for all/specified nodes
def print_routingTable(node):
    routingTable = G.nodes[node]['routingTable'].routing_table
    print("Routing table for %s:" % node)
    for node in routingTable:
        print("\t", node, "\t", routingTable[node])

#ROUTING TABLE CLASS
class RT:

    def __init__(self, node):
        self.name = node
        self.routing_table = {adjacent_node: G.adj[node][adjacent_node]['distance'] for adjacent_node in
                              G.adj[node]}  # add adjacent nodes to the routing table
        non_adjacent_nodes = list(set(G.nodes) - set(G.adj[node]) - set(node))
        self.routing_table.update({non_adj_node: float('infinity') for non_adj_node in
                                   non_adjacent_nodes})  # add non-adjacent nodes to the routing table
        self.routing_table[node] = 0

    def update_edge(self, destination, cost):
        self.routing_table.update({destination: cost})


# Menu displayed to user to show what is available
# command is what the user types in
# argument describes what the command does eg "display help menu"
def menu():
    print("Please type a command:")
    print("     Command                  Argument ")
    print("\thelp or ?                  displays help menu displaying valid commands")
    print("\ttrace N2 N3 N4/all          a Routing Table for the specified nodes is returned")
    print("\troute N1 N4                 The best route between two specified nodes is found")
    print(
        "\texchange 4/stable           compute routing tables for any number of exchanges of until stability is achieved")
    print("\tcost source destination 3/fail        changes the cost of an edge")
    print("\tsplit-horizon               enable Split-Horizon")
    print()
    print("Examples of commands: ")
    print("\texchange 3")
    print("\tcost N1 N4 fail")
    print("\ttrace all")

# User input is separated into a command and arguments and returned
def user_input():
    user = raw_input("> ")
    cmd = user.split(" ")[0]
    args = user.split(" ")[1:]
    return cmd, args


# Checks all argument to see if they are valid or empty, and returns false if so
def argument_check(args, cmd, expected=None, minimum=None, nodes=None, keyword=None, keyword_pos=None):
    if minimum != None and len(args) < minimum:  # check that there is at least min arguments
        print("%s requires at least  %s arguments - type 'help' to see an example" % (cmd, minimum))
        return False
    if expected != None and len(args) != expected:  # checks expected number of arguments are present
        print("%s requires %s arguments - type 'help' to see an example" % (cmd, expected))
        return False
    if keyword != None:  # keyword and position is checked
        if not keyword_check(args, cmd, keyword, keyword_pos):
            print("Argument is invalid, please try again")
            return False
    if nodes != None:  # checks nodes given by the user exist in the graph
        for node in nodes:
            if node not in G.nodes:
                print("%s is not a node in the graph - all arguments must be nodes in the graph. Please try again." % node)
                return False
    return True


# checks if a keyword is being correctly used
def keyword_check(args, cmd, keyword, keyword_pos):
    return number_check(args[keyword_pos]) or node_check(args[keyword_pos]) or args[keyword_pos] == keyword


def number_check(var):
    try:
        float(var)
    except ValueError:
        return False
    return True

# checks node is in graph
def node_check(var):
    return var in G


#  path between nodes is printed
def print_path(path):
    for node in path[:-1]:
        print(node, " -> ", )
    print(path[-1])

#  update Routing Table
def update_routingTable(source, destination, cost):
    G.nodes[source]['routingTable'].update_edge(destination, cost)
    G.nodes[destination]['routingTable'].update_edge(source, cost)


# Routing table is sent to the nodes neighbour
# Routing table gets updated using Bellman Ford to find shortest path
def bellmanFord():
    for source in G.nodes:
        for adjacent in G.adj[source]:
            adjacentNode_RT = G.nodes[adjacent]['routingTable'].routing_table
            source_to_adjacent_distance = G.nodes[source]['routingTable'].routing_table[adjacent]
            for destination in adjacentNode_RT:  # n is a node in the adjacent nodes' routing table
                source_destination_distance = G.nodes[source]['routingTable'].routing_table[destination]
                adj_destination_distance = adjacentNode_RT[destination]

                new_min_distance = min(source_to_adjacent_distance + adj_destination_distance,
                                   source_destination_distance)  # new minimum distance
                G.nodes[source]['routingTable'].update_edge(destination, new_min_distance)
    neg_distance()


def splitHorizon():
    for source in G.nodes:
        for adjacent in G.adj[source]:
            adjacentNode_RT = G.nodes[adjacent]['routingTable'].routing_table
            source_to_adjacent_distance = G.nodes[source]['routingTable'].routing_table[adjacent]
            for destination in adjacentNode_RT:  # n = node in adjacent nodes' routing table
                # Only advertise adjacent nodes
                if destination not in G.adj[source]:
                    source_destination_distance = G.nodes[source]['routingTable'].routing_table[destination]
                    adj_destination_distance = adjacentNode_RT[destination]

                    new_min_distance = min(source_to_adjacent_distance + adj_destination_distance,
                                       source_destination_distance)  # new minimum distance
                    G.nodes[source]['routingTable'].update_edge(destination, new_min_distance)
    neg_distance()

# checks for negative distances between specified nodes
def neg_distance():
    for edge in G.edges:
        if G[edge[0]][edge[1]]['distance'] < 0:
            print("Error: Graph contains a negative edge between %s and %s" % (edge[0], edge[1]))
            sys.exit(0)


nodes_edges = readcsv(args.file)
nodes = nodes_edges[0]
inital_edges = nodes_edges[1:]
edges = format_edges(inital_edges)

# Define Graph, nodes and links between nodes
G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

# Routing table initalised for every node
for node in G.nodes:
    G.nodes[node]['routingTable'] = RT(node)

# Matches user input to commands
print("TO EXIT: enter exit")
cmd, args = user_input()

while cmd not in ["exit", "quit", "stop", "q"]:
    if cmd in ["help", "?"]: # displays help menu to user to show command options
        menu()
        cmd, args = user_input()
    elif cmd == "trace":
        if argument_check(args, cmd, minimum=1, nodes=args[1:], keyword="all", keyword_pos=0):
            if args[0] == "all":
                for node in G.nodes:
                    print_routingTable(node)
                    print()
            else:
                for arg in args:
                    print_routingTable(arg)
                    print()
        cmd, args = user_input()
    elif cmd == "route":
        if argument_check(args, cmd, expected=2, nodes=args):
            source = args[0]
            destination = args[1]
            try:
                path = nx.shortest_path(G, source, destination, weight="distance")
                print("The shortest path between %s and %s : " % (source, destination)) # prints shortest path between specified nodes
                print_path(path)
            except nx.NetworkXNoPath:
                print("No path between %s and %s exists" % (source, destination)) # prints if no path exists between specified nodes
        cmd, args = user_input()
    elif cmd == "cost":
        if argument_check(args, cmd, nodes=args[:-1], expected=3, keyword="fail", keyword_pos=2):
            source = args[0]
            destination = args[1]
            cost = args[2]
            # edges removed if they exist
            if (source, destination) in G.edges:
                G.remove_edge(source, destination)
            if cost == "fail":
                cost = 'infinity'
            update_routingTable(source, destination, float(cost))
            G.add_edges_from([(source, destination, {'distance': float(cost)})])
            print(G.edges.items())
        cmd, args = user_input()
    elif cmd == "exchange":
        if argument_check(args, cmd, expected=1, keyword="stable", keyword_pos=0):
            iteration = int(args[0]) if args[0] != "stable" else len(G.nodes) - 1  # iterations = number of iterations
            for i in range(iteration):  # it takes |V| - 1 iterations for stability where |V| =  number of vertices
                splitHorizon() if SPLIT_HRZN else bellmanFord()
        cmd, args = user_input()
    elif cmd == "split-horizon":
        SPLIT_HRZN = not SPLIT_HRZN  # split horizon toggled
        print("Split horizon has been %s" % 'enabled' if SPLIT_HRZN else 'disabled')
        cmd, args = user_input()
    else:
        if len(cmd.replace(' ', '')) > 0:
            print("%s is an invalid command, type 'help' to display the list of commands available" % cmd)
        cmd, args = user_input()

