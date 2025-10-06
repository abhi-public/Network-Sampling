# Freedman-Diaconis’s Rule: https://www.statisticshowto.com/choose-bin-sizes-statistics/


import numpy as np
import math
import sys
# Raw degree distribution histogram with degree -> frequency
# Create using RawHistogramFromNetwork.py

data_dir = "My_DataFilesPy/"
# data_file = "email-Eu-core_Histogram.csv"
data_file = "musae_DE_Histogram.csv"
all_sample_sizes = [0.1, 0.2, 0.3]  # Fraction of the real size. 10%, 20%, 30%.

# Sample sizes are 10%, 20%, and 30%


if __name__ == "__main__":
    fname = data_dir + data_file
    print(f"data_file={data_file}")
    fin = open(fname , "r")
    h_line = fin.readline()  # Skip the first line if it has text, otherwise not
    f_line =''
    if 'degree' in h_line:
    # if h_line.index('degree') > -1:
        f_line = fin.readline()
    else:
        f_line = h_line
    degree_list = []
    degree_freq_dict = {}
    frequency_list = list()
    while f_line:
        data = f_line.strip().split(",")
        degree_list.append(int(data[0]))
        frequency_list.append(int(data[1]))
        if int(data[0]) in degree_freq_dict:
            print(f"the key exists {data[0]}")
        degree_freq_dict.update({int(data[0]):int(data[1])})
        f_line = fin.readline()
    fin.close()
    print(f"length of degree_list={len(degree_list)}, and frequency_list={len(frequency_list)}")
    Q1 = int(np.median(degree_list[:int(len(degree_list)/2)]))
    Q3 = int(np.median(degree_list[int(len(degree_list)/2)+1:]))
    print(f"Q1={Q1}, Q3={Q3}")
    sum_in_IQR = 0
    N = 0
    for degree,freq in degree_freq_dict.items():
        N = N + freq
        if Q1 <= degree <= Q3:
            sum_in_IQR = sum_in_IQR + freq
    print(f"sum in the QAR={sum_in_IQR}, N={N}")
    bin_size = 2*(Q3-Q1)/pow(sum_in_IQR,float(1/3))
    print(f"bin_size={bin_size}")
    max_degree = degree_list[-1]
    num_buckets = int(max_degree/bin_size)+1
    # print(f"no_of_bins={no_of_bins}")
    # Start creating the bins
    bins = list(np.linspace(0, max_degree, num=num_buckets, endpoint=False))
    bin_index_list = list(np.digitize(degree_list, bins, right=False))
    print(f"len(bins)={len(bins)}, {bins}")
    print(f"length of bin_index_list={len(bin_index_list)},  min ={min(bin_index_list)}")
    print(f"bin_index={bin_index_list}")
    print(f"min bin index ={min(bin_index_list)}")
    # Adding the last bin for padding (0), this will always be added because bins contain the lower bounds of all buckets.
    if float(np.max(bins)) <= max_degree:
        bins.append(max_degree + 1)
    new_frequency = [0] * len(bins)
    # print(f"histogram_buckets={histogram_buckets}")
    sum_nodes = 0
    for i in range(0, len(bin_index_list)):
        bin_index = bin_index_list[i]
        # print(f"bin_index={bin_index}")
        frequency = frequency_list[i]
        sum_nodes = sum_nodes + frequency
        new_frequency[bin_index - 1] = new_frequency[bin_index - 1] + frequency
        # print(f"bin_index={bin_index}, frequency={frequency}, new_frequency[bin_index-1]={new_frequency[bin_index-1]}")
    print(f"number of bins with non-zero values={len(set(bin_index_list))}")
    print(f'sum_nodes={sum_nodes}')
    for i in range(len(bins)):
        print(f"bin {i}--> {bins[i]}  :  {new_frequency[i]}")
    rel_degree_frequency = dict()
    sum_n = 0
    upper_bounds_list = list()
    for i, b in enumerate(bins):
        rel_degree = float(b) / float(N)
        frequency = new_frequency[i]
        rel_degree_frequency.update({rel_degree: frequency})
        if i == len(bins) - 1:
            upper_bounds_list.append(1.0)
        else:
            upper_bounds_list.append(float(bins[i + 1] * 0.9999999999) / float(N))
    rel_hist_filename = data_dir + data_file.replace(".csv", "_FD_rel.csv")
    rel_hist_out = open(rel_hist_filename, "w")

    ctr = 0
    for b in rel_degree_frequency:
        freq = rel_degree_frequency.get(b)
        #  Add all the bins, even when the freq is 0.
        rel_hist_out.write(str(b) + "," + str(upper_bounds_list[ctr]) + "," + str(freq) + "\n")
        ctr += 1
        sum_n = sum_n + freq
        print(f"bin={b} : {freq}")
    print(f"n={N}, sum_n={sum_n}")
    rel_hist_out.close()

    # Create the dat files. In this file, we get all bins including 0
    # print(f"finding histogram in name={data_file.lower().find('histogram')}")
    edge_file_name = data_file[0:data_file.lower().find("histogram") - 1]
    # edge_file_name = data_file[0:data_file.lower().find("pr.csv") - 1]
    if data_file.lower().find("csv") == -1:
        print('fix the name, change it appropriately')
        sys.exit()
    for sample_size in all_sample_sizes:
        # Added later on Nov 9, 2021
        # if sum_n * sample_size > 12000:
        #     sample_size = float(12000) / sum_n
        suffix = str(int(np.ceil(sum_n * sample_size))) + "N" + str(len(rel_degree_frequency)) + "B_FD.dat"
        dat_file_name = data_dir + edge_file_name + "-" + suffix
        print(f"dat_file_name={dat_file_name}")
        dat_out = open(dat_file_name, "w")
        dat_out.write("@RangesStart\n")
        line = ""
        nk_list = list()
        for b in rel_degree_frequency:
            line = line + str(b) + ","
            nk_list.append(round(rel_degree_frequency.get(b) * sample_size, 2))
        line = line[:-1]
        dat_out.write("l:" + line + "\n")
        line = ""
        for b in upper_bounds_list:
            line = line + str(b) + ","
        line = line[:-1]
        dat_out.write("u:" + line + "\n")
        dat_out.write("@RangesEnd\n")
        total = 0
        sum_leaving_last = 0
        for i, ele in enumerate(nk_list):
            # print(f"ele={ele}")
            total = total + round(ele, 2)
            if i < len(nk_list) - 2:
                sum_leaving_last = sum_leaving_last + ele  # total up to and including n-3, n-2 needs to be changed, n-1 is padding 0, n = length.
        # print(f"len(nk_list)={len(nk_list)}, nk_list[len(nk_list)-2]={nk_list[len(nk_list) - 2]}")
        final_n = math.ceil(total)
        # print(f"final_n,{final_n}, sum_leaving_last={round(sum_leaving_last,2)}, nk_list={nk_list}")
        corrected_value = round(final_n - sum_leaving_last, 2)
        nk_list[len(nk_list) - 2] = corrected_value
        print(f"len(nk_list)={len(nk_list)}, nk_list[len(nk_list)-2]={corrected_value}")
        dat_out.write("n:" + str(final_n) + "\n")
        nk_line = ""
        for e in nk_list:
            nk_line = nk_line + str(e) + ","
        nk_line = nk_line[:-1]
        dat_out.write("nk:" + nk_line + "\n")
        dat_out.write("######### Ignore reading after this ############ Information only\n")
        dat_out.write(
            f"bucket size=FD's (Freedman-Diaconis) rule, number of buckets={len(bins) - 1}+1 padding, delimiter in original file='-'")
        dat_out.close()

    print("done..")

