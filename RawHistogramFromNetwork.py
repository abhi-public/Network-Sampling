import networkx as nx
import sys
import os


def degree_node(myGraph, logfile, myfilename):
    degree_nodes_dict = dict()
    print('creating the histogram now, processing nodes.')
    for n in myGraph.nodes():
        degree = myGraph.degree[n]
        if degree in degree_nodes_dict:
            nodes_list = degree_nodes_dict.get(degree)
            nodes_list.append(n)
            degree_nodes_dict.update({degree: nodes_list})
        else:
            nodes_list = []
            nodes_list.append(n)
            degree_nodes_dict.update({degree: nodes_list})
    sorted_degrees = sorted(degree_nodes_dict)
    print('creating histogram now.')
    logfile.write(f"degree,frequency\n")
    hist_csv = open(f'{os.path.splitext(myfilename)[0].replace("_pr", "_Histogram")}.csv', 'w')
    for degree in sorted_degrees:
        # print(f"degree={degree}, nodes={degree_nodes_dict.get(degree)}")
        logfile.write(f"{degree},{len(degree_nodes_dict.get(degree))}\n")
        hist_csv.write(f"{degree},{len(degree_nodes_dict.get(degree))}\n")
    logfile.write(f"--------\n")
    hist_csv.close()



if __name__ == "__main__":
    # Read the graph
    mydir = 'My_DataFilesPy/'
    logfilepath = 'Logs/'

    foutlog = open(logfilepath + "RawHistogram.log", "w")
    NumEdges = 0
    # NetFileName = "My_DataFilesPy/email-Eu-core_pr.ed"
    NetFileName = mydir + "musae_DE_pr.ed"


    print('Creating the graph now.')
    myGraph = nx.Graph()
    edge_fin = open(NetFileName, "rt")
    line = edge_fin.readline()
    while line:
        line = line.strip()

        if "%" not in line and line.find("-") > -1:
            NumEdges += 1
            nodes = line.split("-")
            if myGraph.has_edge(int(nodes[0]), int(nodes[1])) is False:
                myGraph.add_edge(int(nodes[0]), int(nodes[1]))
        else:
            if myGraph.has_node(int(line)) is False:
                myGraph.add_node(int(line))
        line = edge_fin.readline()
    edge_fin.close()
    print("Read the graph into networkx")
    degree_node(myGraph, foutlog, NetFileName)
    if NumEdges != myGraph.number_of_edges():
        print("number of edges not matching, NumEdges=", NumEdges, "from graph", myGraph.number_of_edges())
        sys.exit()
    print("NetFileName=", NetFileName, "NumEdges=", NumEdges)
    foutlog.write(f"NetFileName={NetFileName}, NumEdges={NumEdges}\n")
    foutlog.close()