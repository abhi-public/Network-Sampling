'''
I keep all utility functions here to avoid clutter in the main files.
'''


# The bin or band numbers start from 1 not 0.
def get_bin_numbers(bins, node_neighbor_dict, net_size):
    node_bin_dict = dict()
    bins_number_set = set()
    # print("bins=", bins)
    bins_membership_dict = dict()
    bin_member_dict = dict()  # bin # : list(members)
    for n in node_neighbor_dict:
        rel_degree = float(len(node_neighbor_dict.get(n))/net_size)
        added = 0
        for indx, bound in enumerate(bins, start=1):
            # print("indx=", indx, "bound=", bound, "relative degree=", rel_degree)
            if rel_degree < bound:
                # print("adding band=", (indx-1))
                node_bin_dict.update({n: indx-1})
                bins_number_set.add(indx-1)
                added = 1
                if (indx-1) in bin_member_dict:
                    m_list = bin_member_dict.get(indx-1)
                    m_list.append(int(n))
                    bin_member_dict.update({indx-1: m_list})
                else:
                    m_list = [int(n)]
                    bin_member_dict.update({indx - 1: m_list})
                break
        if added == 0:
            node_bin_dict.update({n: len(bins)})
            bins_number_set.add(len(bins))
            if (len(bins)) in bin_member_dict:
                m_list = bin_member_dict.get(len(bins))
                m_list.append(int(n))
                bin_member_dict.update({len(bins): m_list})
            else:
                m_list = [int(n)]
                bin_member_dict.update({len(bins): m_list})
    for n in node_bin_dict:
        bin_number = node_bin_dict.get(n)
        bins_membership_dict[bin_number] = bins_membership_dict.get(bin_number, 0) + 1  # return 0 if the key is not present
    # for n in orig_node_neighbor_dict:
    #     print("node=", n)
    #     bin = node_bin_dict.get(n)
    #     print("node=", n, "bin=", bin)
    # print("bins_membership_dict=", bins_membership_dict)
    return node_bin_dict, bins_membership_dict, bin_member_dict

# This method may require mofocation based on the structure of the file
def convert_to_csv(filename, separator):
    file_in = open(filename, "r")
    name_to_use = filename[:filename.rfind(".")]
    file_out = open(name_to_use + ".csv", "w")
    line = file_in.readline()
    while line:
        new_line = line.strip().replace(separator, ",")
        file_out.write(new_line + "\n")
        line = file_in.readline()
    file_out.close()


if __name__ == "__main__":
    bins = ""
    node_neighbor_dict = dict()
    net_size = 0
    # get_bin_numbers(bins, node_neighbor_dict, net_size)
    filename = "C:/Work2/Dropbox/Work2/NetworkSampling/DataFilesPy/RawDataset/gplus_combined.txt"
    convert_to_csv(filename, " ")