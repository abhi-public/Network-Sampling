'''
This program implements a simple heuristic that goes band by band to select nodes for deletion.
The base file is Heuristics_lb_dist, with comments and streamlined code. Specifically, I am trying to make this code close to the
final algorithm.

In the final edge file, lone nodes are excluded because we write edges.
'''

# from NetSampleFormulation import NetSampleIPMain as pdf
# from NetSampleFormulation import NetSample_KS_IPMain as cdf
# from Analysis.FindAttributes import *
import sys
import Utility_Functions as uf
import numpy as np
import networkx as nx
# import math
from datetime import datetime, date


args_fname = "Args/Setup_NetSamplingHeu_FD.arg"
m = 4  # number of mini-batches
ws_m = 8
# number of micro-batches
micro_batch = 5
micro_batch_ws = 15
# If we just want to use batches only and no micro-batches
number_of_batches = 5


# Choose heuristic type
using_heuristic_type = "HyBD"  # Hybrid
# using_heuristic_type = "BD"  # Batch deletion


def ReadNetwork(ParamList):
    dataDir = ParamList[0]
    edgeFileFullName = ParamList[2]
    NetFileName = dataDir + "/" + edgeFileFullName
    # Read the graph
    NumEdges = 0
    myGraph = nx.Graph()
    edge_fin = open(NetFileName, "rt")
    line = edge_fin.readline()
    while line:
        line = line.strip()
        if line.find("-") > -1:
            NumEdges += 1
            nodes = line.split("-")
            myGraph.add_edge(int(nodes[0]), int(nodes[1]))
        else:
            myGraph.add_node(int(line))
        line = edge_fin.readline()
    edge_fin.close()
    if NumEdges != myGraph.number_of_edges():
        print("number of edges not matching, NumEdges=", NumEdges, "from graph", myGraph.number_of_edges(), ". Are there duplicate edges?")
        # sys.exit()

    print("NetFileName=", NetFileName, "NumEdges=", NumEdges)

    # print("Trial")
    return myGraph


def ReadIPParameters(IPParamsFileName):
    fInIPParams = open(IPParamsFileName, "rt")
    fInIPParams.readline().strip()  # Skip
    line = fInIPParams.readline().strip()
    lb = line[line.find(":") + 1:].strip().split(",")
    line = fInIPParams.readline().strip()
    ub = line[line.find(":") + 1:].strip().split(",")
    fInIPParams.readline()  # Skip
    line = fInIPParams.readline().strip()
    n = int(line[line.find(":") + 1:].strip())
    line = fInIPParams.readline().strip()
    nk = line[line.find(":") + 1:].strip().split(",")
    IPParams = [lb, ub, n, nk]
    # print("IPParams=", IPParams)
    fInIPParams.close()
    return IPParams


# Mini batch and microbatch creation.
def stop_points_heu_hybrid_default(len_deletion: int):
    stop_points_list = [0] # Ensure a 0 in the list because first time run in a band is necessary.

    for i in range(m):
        stop_points_list.append(int(len_deletion/m)*i)
    print(f"Mini batch and micro batch: number of deletions needed={len_deletion}, stop points={stop_points_list}")
    # For the last 25%, add at the intervals of 5%
    starting = int(len_deletion*(m-1)/m)
    size = micro_batch
    piece_size = (len_deletion/m)
    for i in range(size-1):
        stop_points_list.append(starting + int(piece_size/size)*(i+1))
    print(f"Mini batch and micro batch: number of deletions needed={len_deletion}, stop points={stop_points_list}")
    return list(set(stop_points_list)) # Removed duplicates
# stop_points_heu_hybrid(18123)

def stop_points_heu_hybrid_ws(len_deletion: int):
    print(f'Stepping inside ws special list of stopping point. Tuning for more revisions in the beginning')
    stop_points_list = []
    start_mini_batch = 0
    stop_mini_batch = int(len_deletion / 2)
    len_mini_batch = max(1,int((stop_mini_batch - start_mini_batch) / ws_m)) # Sometimes the value becomes 0 otherwise.
    # Create mini batches
    for i in range(start_mini_batch, stop_mini_batch, len_mini_batch):
        stop_points_list.append(i)
    print(f'stop_points_list={stop_points_list}')

    # Insert micro-batches
    start_micro_batch = int(len_deletion / 2)
    stop_micro_batch = len_deletion
    len_micro_batch = max(int((stop_micro_batch - start_micro_batch) / micro_batch_ws),1) # Sometimes the value becomes 0 otherwise.

    for i in range(start_micro_batch, stop_micro_batch, len_micro_batch):
        stop_points_list.append(i)
    print(f'stop_points_list={stop_points_list}')
    print(f"Mini batch and micro batch: number of deletions needed={len_deletion}, stop points={stop_points_list}")
    return list(set(stop_points_list)) # Removed duplicates

# Mini batch creation.
def stop_points_heu_batch_processing(len_deletion: int, no_of_batches: int):
    stop_points_list = list()
    for i in range(no_of_batches):
        stop_points_list.append(int(len_deletion/no_of_batches)*i)
    print(f"Mini batch only: number of deletions needed={len_deletion}, stop points={stop_points_list}")
    return stop_points_list


# noinspection PyShadowingNames
def main_heuristic_BD(orig_network, IP_params):
    # STOP_PROCEESS = False
    sample_graph = orig_network.copy(as_view=False)
    # sample_node_neighbor_dict = dict(node_neighbor_dict)
    bins_str = IP_params[0]
    bins = [float(x) for x in bins_str]
    # Iterating through the bins
    n_vals = IP_params[3]
    highest_band = len(n_vals)
    # final_correction_band = highest_band

    # if int(float(n_vals[highest_band-1])) == 0:  # The last band with number "highest_band" has 0 nodes, which means this is a buffer band.
    #     final_correction_band = highest_band - 1
    for band in range(1, highest_band + 1):  # I am intentionally not using the keys of bins_membership_dict because this dictionary is useless right now
        # print("------------- New loop for band=", band, "type", type(band))
        #  Check whether we have to stop the entire process. For example, have we reached the desired size for the sample?
        # if STOP_PROCEESS:
        #     print(f"breaking at band={band}")
        #     break
        sample_node_neighbor_dict = dict()
        # Creating nodes and neighbors dictionary
        for node in list(sample_graph.nodes()):
            neighbors = list(sample_graph.adj[int(node)])
            sample_node_neighbor_dict.update({str(node): neighbors})
        network_size = float(len(sample_graph.nodes()))
        # 3. Update the histogram with current intermediate sample.
        # Also, collect sample node -> bin map, sample bin -> membership number map, and bin -> members map
        sample_node_bin_dict, sample_bins_membership_dict, bin_member_dict = uf.get_bin_numbers(bins, sample_node_neighbor_dict, network_size)
        # print("sample_bins_membership_dict=", sample_bins_membership_dict)
        '''
        # 4. Find the list of nodes in each bin - a redundant step at this point.
        band_neignbors_dict = dict()
        for node, b in sample_node_bin_dict.items():
            # print("node, b", node, b)
            if int(b) in band_neignbors_dict:
                # print("prioir node_list=", node_list)
                node_list = band_neignbors_dict.get(int(b))
                node_list.append(int(node))
                # print("new node_list=", node_list)
                band_neignbors_dict.update({int(b): node_list})
            else:
                node_list = [int(node)]
                band_neignbors_dict.update({int(b): node_list})

        # for band, members in band_neignbors_dict.items():
        #     print("band=", band, "members=", members)
        
        # 5. Get the list of nodes in the band of interest (k)
        members = band_neignbors_dict.get(band)
        '''
        members = bin_member_dict.get(band)
        # print("members=", members)
        # 6. Go to the next bin if no members exist.
        if members is None:
            continue

        # Determine delta for this band
        # actual_till_prev_band = 0
        # required_till_prev_band = 0

        # ---------------------
        # Checking whether the processes create different numbers
        target_cum = 0
        actual_cum = 0
        # number_to_delete = 0
        for i in range(1, band+1):  # Calculate up to the previous band
            # node_list = band_neignbors_dict.get(i)
            node_list = bin_member_dict.get(i)
            # print("band", band, "i number", i, "node_list", node_list)
            if node_list is not None:
                actual_cum = actual_cum + len(node_list)
            target_cum = target_cum + float(n_vals[i - 1])
        zeta_delete1 = round(float(actual_cum) - float(target_cum))
        zeta_delete2 = len(members)
        zeta_delete3 = int(network_size - float(IP_params[2]))
        zeta_delete = min(zeta_delete1, zeta_delete2, zeta_delete3)
        # zeta_delete = min(zeta_delete1, zeta_delete2)
        # zeta_delete = zeta_delete1
        if zeta_delete < 0:
            zeta_delete = 0

        number_to_delete = int(zeta_delete)
        # logs.write(f"zeta_delete1 = {zeta_delete1}, zeta_delete2={zeta_delete2}\n")
        # if zeta_delete == zeta_delete1:
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == zeta_delete1\n")
        # if zeta_delete == len(members):
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == len(members)\n")
        # if zeta_delete == zeta_delete3:
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == zeta_delete3\n")
        # ----------------------------------------------
        # 7. Calculate deviation up to the previous bin
        # If the members have sufficient number of nodes (greater than what to delete), then find the number.
        # Otherwise, make the number to delete =0 (skip this bin).

        # for i in range(1, band):  # Calculate up to the previous band
        #     # node_list = band_neignbors_dict.get(i)
        #     node_list = bin_member_dict.get(i)
        #     # print("band", band, "i number", i, "node_list", node_list)
        #     if node_list is not None:
        #         actual_till_prev_band = actual_till_prev_band + len(node_list)
        #     required_till_prev_band = required_till_prev_band + float(n_vals[i - 1])
        # deviation_till_prev_band = float(actual_till_prev_band) - float(required_till_prev_band)
        # print("deviation so far=", deviation_till_prev_band)
        # logs.write(f"deviation so far= {deviation_till_prev_band}\n")
        # # If the members have sufficient number of nodes (greater than what to delete), then find the number.
        # # Otherwise, make the number to delete =0 (skip this bin).
        # if len(members) > float(n_vals[band - 1]) + deviation_till_prev_band:
        #     number_to_delete = round(len(members) - float(n_vals[band - 1]) + deviation_till_prev_band)
        #     if zeta_delete1 >0 and zeta_delete1 != number_to_delete:
        #         print(f"number_to_delete={number_to_delete} and zeta_delete1 = {zeta_delete1}")
        #         sys.exit(0)
        # else:
        #     number_to_delete = 0

        # Looping through the members
        member_score_dict = dict()
        # 8. Calculate the scores of all the nodes in the member (nodes in the bin).
        for node in members:
            score = distance_for_score(node, sample_node_bin_dict, sample_graph, IP_params)
            member_score_dict.update({node: score})
        # 9. Sort the nodes based on the scores.
        sorted_member_score_tuple = sorted(member_score_dict.items(), key=lambda x: x[1], reverse=True)
        # print("Current membership in band", band, "is", float(sample_bins_membership_dict.get(band)), "type is", type(sample_bins_membership_dict.get(band)) , ", float(n_vals[band - 1])=", float(n_vals[band - 1]))
        # print(float(sample_bins_membership_dict.get(band)) - float(n_vals[band - 1]) + deviation)
        # print("len(members)=", len(members), "float(n_vals[band - 1])=", float(n_vals[band - 1]), "deviation_till_prev_band", deviation_till_prev_band)



        # 11. Correct the numbers to delete for the last band K. If the last band does not contain sufficient number of
        # nodes to delete, then go for another pass starting from bin 1. Do not delete anything right now.
        # if band == final_correction_band:
        #     total_so_far = 0
        #     for band1, membership_no in sample_bins_membership_dict.items():
        #         if band1 < final_correction_band:
        #             total_so_far = total_so_far + float(membership_no)
        #     total_needed_now = float(IP_params[2]) - total_so_far
        #     if len(members) > total_needed_now:
        #         number_to_delete = round(len(members) - total_needed_now)
        #     else:
        #         number_to_delete = 0
        #     print("new number_to_delete=", number_to_delete)
        #     logs.write(f"new number_to_delete= {number_to_delete}\n")

        deleted_nodes = []
        # 12. Start deleting nodes in a loop until the required number of nodes are deleted.
        for i in range(number_to_delete):
            # 12 -> 13. If all nodes in the bin are already deleted, stop this loop.
            # if len(sorted_member_score_tuple) == i:
            #     print(f"breaking because the members list is empty now.")
            #     logs.write(f"breaking because the members list is empty now at {i}\n")
            #     break
            # print(f"iteration {i}, length of sorted_member_score_tuple={len(sorted_member_score_tuple)}")
            # 12 -> 14. Delete the next node in the bin.
            tuple_members = str(sorted_member_score_tuple[i])
            member_to_delete = int(tuple_members[1: tuple_members.find(",")].strip())
            # print("Removing node", member_to_delete, " from band", band)
            # logs.write("Removing node" + str(member_to_delete) + " from band " + str(band) + "\n")
            sample_graph.remove_node(member_to_delete)
            deleted_nodes.append(str(sorted_member_score_tuple[i]))
            # 12 -> 15. If we have already obtined the sample of required size, stop the process of deletion.
            # if len(list(sample_graph.nodes())) <= float(IP_params[2]):
            #     STOP_PROCEESS = True
            #     break
        # logs.write("Removing node" + str(deleted_nodes) + " from band " + str(band) + "\n")
        # print("nodes deleted", deleted_nodes, "from band", band)
    return sample_graph


# This heuristic is a mix of h1 and h2 above. h1 deletes all the nodes at once from the band and then revises the graph. This causes too much
# deviation. h2 revises the graph after every deletion making it very slow. In this heuristic, we delete in small batches and revise the graph
# after deleting nodes in each batch. This provides a middle ground between h1 and h2. The function "stop_points_heu_hybrid" provides the counters
# at which revision should happen.
# This same code can handle batch processing as well.

# noinspection PyShadowingNames
def main_heuristic_hybrid(orig_network, IP_params, use_batch_processing, ws_batch = 0):
    # Variable to stop the entire process of sample creation
    # STOP_PROCEESS = False
    sample_graph = orig_network.copy(as_view=False)
    # sample_node_neighbor_dict = dict(node_neighbor_dict)
    bins_str = IP_params[0]
    bins = [float(x) for x in bins_str]
    # Looping through the bins
    n_vals = IP_params[3]
    highest_band = len(n_vals)
    # final_correction_band = highest_band

    # if int(float(n_vals[highest_band-1])) == 0:  # The last band with number "highest_band" has 0 nodes, which means this is a buffer band.
    #     final_correction_band = highest_band - 1
    # Iterating through the bins 1 to K.
    bin_nodes_del_map = {}
    for band in range(1, highest_band + 1):
        # print("------------- New loop for band=", band, "type", type(band))
        # 1. Check criteria to run the passes.
        # if STOP_PROCEESS:
        #     print(f"breaking at band={band}")
        #     break
        sample_node_neighbor_dict = dict()
        # 2. Creating nodes and neighbors dictionary
        for node in list(sample_graph.nodes()):
            neighbors = list(sample_graph.adj[int(node)])
            sample_node_neighbor_dict.update({str(node): neighbors})
        network_size = float(len(sample_graph.nodes()))
        # 3. Update the histogram with corrent intermediate sample.
        sample_node_bin_dict, sample_bins_membership_dict, bin_member_dict = uf.get_bin_numbers(bins, sample_node_neighbor_dict, network_size)
        # print("sample_bins_membership_dict=", sample_bins_membership_dict)
        # 4. Find the list of nodes in each bin - a redundant step at this point.
        # band_neighbors_dict = dict()
        # for node, b in sample_node_bin_dict.items():
        #     # print("node, b", node, b)
        #     if int(b) in band_neighbors_dict:
        #         # print("prioir node_list=", node_list)
        #         node_list = band_neighbors_dict.get(int(b))
        #         node_list.append(int(node))
        #         # print("new node_list=", node_list)
        #         band_neighbors_dict.update({int(b): node_list})
        #     else:
        #         node_list = [int(node)]
        #         band_neighbors_dict.update({int(b): node_list})
        # # for band, members in band_neignbors_dict.items():
        # #     print("band=", band, "members=", members)
        # # 5. Get the list of nodes in the band of interest (k)
        # members = band_neighbors_dict.get(band)
        members = bin_member_dict.get(band)
        # print("members=", members)
        # 6. Go to the next bin if no members exist.
        if members is None:
            continue
        # print("band=", band, "members=", members)
        # Determine zeta_delete for this band
        # ---------------------
        target_cum = 0
        actual_cum = 0
        # number_to_delete = 0
        for i in range(1, band + 1):  # Calculate up to the previous band
            # node_list = band_neignbors_dict.get(i)
            node_list = bin_member_dict.get(i)
            # print("band", band, "i number", i, "node_list", node_list)
            if node_list is not None:
                actual_cum = actual_cum + len(node_list)
            target_cum = target_cum + float(n_vals[i - 1])
        zeta_delete1 = round(float(actual_cum) - float(target_cum))
        zeta_delete2 = len(members)
        zeta_delete3 = int(network_size - float(IP_params[2]))
        zeta_delete = min(zeta_delete1, zeta_delete2, zeta_delete3)
        # zeta_delete = min(zeta_delete1, zeta_delete2)
        # zeta_delete = zeta_delete1
        if zeta_delete < 0:
            zeta_delete = 0
        number_to_delete = int(zeta_delete)
        # logs.write(f"zeta_delete1 = {zeta_delete1}, zeta_delete2={zeta_delete2}\n")
        # if zeta_delete == zeta_delete1:
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == zeta_delete1\n")
        # if zeta_delete == len(members):
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == len(members)\n")
        # if zeta_delete == zeta_delete3:
        #     logs.write(f"zeta_delete = {zeta_delete}, zeta_delete == zeta_delete3\n")
        # ----------------------------------------------
        # actual_till_prev_band = 0
        # required_till_prev_band = 0
        # # 7. Calculate deviation up to the previous bin
        # for i in range(1, band):  # Calculate up to the previous band
        #     # node_list = band_neighbors_dict.get(i)
        #     node_list = bin_member_dict.get(i)
        #     # print("band", band, "i number", i, "node_list", node_list)
        #     if node_list is not None:
        #         actual_till_prev_band = actual_till_prev_band + len(node_list)
        #     required_till_prev_band = required_till_prev_band + float(n_vals[i - 1])
        # deviation_till_prev_band = float(actual_till_prev_band) - float(required_till_prev_band)
        #
        # print("deviation so far=", deviation_till_prev_band)
        # logs.write(f"deviation so far= {deviation_till_prev_band}\n")
        # # Looping through the members
        # print("len(members)=", len(members), "float(n_vals[band - 1])=", float(n_vals[band - 1]), "deviation_till_prev_band", deviation_till_prev_band)
        # # 8. If the members have sufficient number of nodes (greater than what to delete), then find the number.
        # # Otherwise, make the number to delete =0 (skip this bin).
        # if len(members) > float(n_vals[band - 1]) + deviation_till_prev_band:
        #     number_to_delete = round(len(members) - float(n_vals[band - 1]) + deviation_till_prev_band)
        # else:
        #     number_to_delete = 0
        # logs.write(f"number_to_delete= {number_to_delete}\n")
        # 9. Correct the numbers to delete for the last band K. If the last band does not contain sufficient number of
        # nodes to delete, then go for another pass starting from bin 1. Do not delete anything right now.
        # if band == final_correction_band:
        #     total_so_far = 0
        #     for band1, membership_no in sample_bins_membership_dict.items():
        #         if band1 < final_correction_band:
        #             total_so_far = total_so_far + float(membership_no)
        #     total_needed_now = float(IP_params[2]) - total_so_far
        #     if len(members) > total_needed_now:
        #         number_to_delete = round(len(members) - total_needed_now)
        #     else:
        #         number_to_delete = 0
        #     print("new number_to_delete=", number_to_delete)
        #     logs.write(f"new number_to_delete= {number_to_delete}\n")
        deleted_nodes = []
        if use_batch_processing == 1:
            stop_points = stop_points_heu_batch_processing(number_to_delete, number_of_batches)
        else:
            if ws_batch == 1:
                stop_points = stop_points_heu_hybrid_ws(number_to_delete)
            else:
                stop_points = stop_points_heu_hybrid_default(number_to_delete)
        # print(f"stop_points={stop_points}")
        sorted_member_score_tuple = tuple()
        # 10. Start deleting nodes in a loop until the required number of nodes are deleted.
        for i in range(number_to_delete):
            # 10 -> 11. If the bin has no more nodes, break out of the loop.
            if len(members) == 0:
                print(f"breaking because the members list is empty now.")
                break
            # if the number of elements in members = 0, then nothing is left to delete now.
            # We implement the batch processing by using a list (stop_points) that contains the values of i at which the histogram is updated.
            # In the list, the difference between two consecuting elements is the size of the batch.
            if i in stop_points:  # Time to revise the scores
                sample_node_neighbor_dict = dict()
                for node in list(sample_graph.nodes()):
                    neighbors = list(sample_graph.adj[int(node)])
                    sample_node_neighbor_dict.update({str(node): neighbors})
                network_size = float(len(sample_graph.nodes()))
                sample_node_bin_dict, sample_bins_membership_dict, bin_member_dict = uf.get_bin_numbers(bins, sample_node_neighbor_dict, network_size)
                member_score_dict = dict() # It should get initialized at i=0 and get revised when needed. Thus, stop_points must contain i=0.
                for node in members:
                    score = distance_for_score(node, sample_node_bin_dict, sample_graph, IP_params)
                    member_score_dict.update({node: score})
                # print(f"Revision of memeber scores performed when i={i}, length of member_score_dict={len(member_score_dict)}, len of member ={len(members)}")
                sorted_member_score_tuple = sorted(member_score_dict.items(), key=lambda x: x[1], reverse=True)

            # print(f"band ={band}, iteration {i}, length of sorted_member_score_tuple={len(sorted_member_score_tuple)}")
            tuple_members = str(sorted_member_score_tuple[0])
            member_to_delete = int(tuple_members[1: tuple_members.find(",")].strip())
            # print("Removing node", member_to_delete, " from band", band)
            # logs.write("Removing node" + str(member_to_delete) + " from band " + str(band) + "\n")
            sample_graph.remove_node(member_to_delete)
            deleted_nodes.append(tuple_members)
            members.remove(member_to_delete)
            sorted_member_score_tuple.pop(0)
        bin_nodes_del_map.update({band:str(len(deleted_nodes)) + "," + str(zeta_delete)+ "," + str(zeta_delete1)+ "," + str(zeta_delete2)+ "," + str(zeta_delete3)})
        # print("nodes deleted", deleted_nodes, "from band", band)
    return sample_graph, bin_nodes_del_map


# noinspection PyShadowingNames
def distance_for_score(node, node_bin_dict, orig_network, IP_params):
    lb = IP_params[0]
    # score = 0
    network_size = float(len(list(orig_network.nodes())))
    distance_list = []
    for neighbor in list(orig_network.adj[node]):
        bin_number = node_bin_dict.get(str(neighbor))
        lb_k = float(lb[bin_number - 1])
        rd = float(len(list(orig_network.adj[neighbor])))/network_size
        # print("band number", bin_number, "lb_k=", lb_k, "rd=", rd)
        dis_lb = rd - lb_k

        distance_list.append(dis_lb)
    average_dist = np.average(distance_list)
    return average_dist


if __name__ == "__main__":
    print("args_fname=", args_fname)
    fInArgs = open(args_fname)
    line = fInArgs.readline().strip()
    # Initial parameters used for choices used later.
    use_batch_processing = 0
    track_extra = 0  # If I want to track something specific, I can use this file.
    ws_batch = 0


    # Read the arguments file
    while line:
        if line.find("#") > -1:
            line = fInArgs.readline().strip()
            continue
        # Time tracking for a particular dataset
        start = datetime.now()
        start_day = date.today()
        # Read the arguments file
        myargs = line.strip().split(" ")
        dataDir = myargs[0]  # Data file path
        IpParamDataFileName = dataDir + "/" + myargs[1]  # contains parameters useful for the IP and program
        print("Data directory =", dataDir, f" file name={myargs[1]}")
        args_suffix = myargs[1][myargs[1].rfind("-")+1:myargs[1].rfind(".")]  # last index found of "."
        print("suffix=", args_suffix)
        edgeFileName = myargs[2]  # contains only edges separated by "-", only the file name without extension
        edgeFileFullName = edgeFileName+".ed"
        localLogDir = myargs[3]  # local directory to store extra file like logs
        if len(myargs) > 4:
            special_arguments = myargs[4]
            if special_arguments == "ws":
                ws_batch = 1
        print(f'ws_batch={ws_batch}')

        # Collect parameters required to identify the important files
        params = list()
        params.append(dataDir)
        params.append(IpParamDataFileName)
        params.append(edgeFileFullName)
        params.append(localLogDir)
        params.append(args_suffix)

        # Main process starting
        print("Reading network")
        orig_net = ReadNetwork(params)
        IP_params = ReadIPParameters(params[1])
        bins_str = IP_params[0]
        bins = [float(x) for x in bins_str]
        node_neighbor_dict = {}
        orig_net_size = float(len(orig_net.nodes()))
        for ni in list(orig_net.nodes()):
            nodeID = str(ni)
            neighbors = list(orig_net.adj[ni])
            node_neighbor_dict.update({nodeID: neighbors})
        node_bin_dict, bins_membership_dict, bin_member_dict = uf.get_bin_numbers(bins, node_neighbor_dict, orig_net_size)
        # print(node_bin_dict)
        # print(bins_membership_dict)
        iteration_number = 1
        required_net_size = float(IP_params[2])
        # sample_graph = main_heuristic1(orig_net, IP_params, foutLog)
        Delta = -1


        # Here we implement the multiple passes through the network until we find the sample of desired size (n).
        deleted_nodes_map_list = []
        while True:
            sample_graph = nx.Graph()
            if using_heuristic_type == "BD":
                sample_graph = main_heuristic_BD(orig_net, IP_params)
            elif using_heuristic_type == "HyBD":
                sample_graph, bin_nodes_del_map = main_heuristic_hybrid(orig_net, IP_params, use_batch_processing, ws_batch)
                deleted_nodes_map_list.append(bin_nodes_del_map)
            else:
                print("Stopping. Choose the correct name of algorithm")
                sys.exit()
            iteration_number += 1
            if len(sample_graph.nodes()) == 0:
                print("Stopping. Sample graph empty")
                sys.exit()
            orig_net = sample_graph
            print(f"Number of nodes after iteration {iteration_number}, is {len(sample_graph.nodes())}")
            print(f"ITERATION NUMBER FOR RUNNING THE HEURISTIC AGAIN IS {iteration_number}")



            # Analyze the sample graph
            bins_str = IP_params[0]
            bins = [float(x) for x in bins_str]
            sample_node_neighbor_dict = dict()
            zero_degree_nodes = list()
            for node in list(sample_graph.nodes()):
                neighbors = list(sample_graph.adj[int(node)])
                if len(neighbors) == 0:
                    zero_degree_nodes.append(node)
                sample_node_neighbor_dict.update({str(node): neighbors})

            network_size = float(len(sample_graph.nodes()))
            sample_node_bin_dict, sample_bins_membership_dict, bin_member_dict = uf.get_bin_numbers(bins, sample_node_neighbor_dict, network_size)
            n_vals = IP_params[3]
            deviations_list = list()

            nk_total = 0
            membership_total = 0
            for indx, nk in enumerate(n_vals):
                nk_total = nk_total + float(nk)
                membership_no = sample_bins_membership_dict.get(indx + 1, 0)
                membership_total = membership_total + membership_no
                # print(f"band={indx + 1}, nk_total={nk_total},membership={membership_no}, membership_total={membership_total}, delta={(membership_total - nk_total)}")
                # foutLog.write(f"band={indx + 1}, nk_total={nk_total},membership={membership_no}, membership_total={membership_total}, delta={(membership_total - nk_total)}\n")

                deviations_list.append(abs(membership_total - nk_total))
            Delta = np.max(deviations_list)
            print(f'Delta={str(Delta)}')

            network_size = len(sample_graph)
            if network_size <= required_net_size:

                break
        if network_size < required_net_size:
            print(f"Problem!!!! We have a network of smaller size than needed: {network_size}. Never found this in testing so far.")
            sys.exit(0)
        output_file_name = ""  # Lone nodes are not written
        if using_heuristic_type == "BD":
            output_file_name = dataDir + "/" + edgeFileName + "-" + args_suffix + ".heu1sample"
        else:
            if use_batch_processing == 1:
                output_file_name = dataDir + "/" + edgeFileName + "-" + args_suffix + ".heu4sample"
            else:
                output_file_name = dataDir + "/" + edgeFileName + "-" + args_suffix + ".heu3sample"
        finish = datetime.now()
        finish_day = date.today()
        graphout = open(output_file_name, "wb")
        nx.write_edgelist(sample_graph, graphout, delimiter=",")
        graphout.close()
        sample_edge_list = list(sample_graph.edges())  # returns a list of tuples (node1, node 2, {name=value})
        connected_nodes = set()
        for e in sample_edge_list:
            connected_nodes.add(e[0])
            connected_nodes.add(e[1])
        print(f"Number of connected nodes = {len(connected_nodes)}")
        print(f"Total number of nodes = {len(sample_graph.nodes())}")
        nodes_file_name = output_file_name[::-1].replace(".", "_", 1)[::-1]+".nodes"   # [::-1] reverses the whole string
        print(f"nodes_file_name={nodes_file_name}")
        fout_nodes = open(nodes_file_name, "w")
        nodes_list_sample = list(sample_graph.nodes())
        for n in nodes_list_sample:
            fout_nodes.write(str(n)+"\n")
        fout_nodes.close()
        print(f"Loop time ={(finish - start).seconds}")
        difference_time = (finish - start).seconds
        difference_days = (finish_day - start_day).days
        print(f"difference_days*24*3600 + difference_time={difference_days*24*3600 + difference_time}")

        print(str(datetime.now()) + "," + "Heuristic_," + args_suffix + "," + ",time_diff=" + str(difference_days*24*3600 + difference_time))

        counter = 1
        for item in deleted_nodes_map_list:
            counter = counter + 1
            for key in item:
                value = item[key]

        line = fInArgs.readline().strip()
    fInArgs.close()
    print("Heuristic for network sampling Done...")
