This file contains instructions about running the sampling program. The program requires specific inputs in specific formats to run properly. 
All programs are written in python. It is useful to create a dedicated anaconda environment and install the packages described below before running the program.


Python packages required are the following. Use anaconda installations.
network
numpy
datetime
sys
math
os

Required files for the sampling program:
1. Edge file
2. Parameters file.
2.1 Parameters file requires a histogram file.
3. Arg file (containing information for the sampling program about the location of data file, logs file, etc.



Edge file:
1. The "edge file" should have edges not repeated, undirected, separated with a "-" (single dash), and the file should have the extension of "<some file name>_pr.ed". For example
1-2
1-18
1-317
1-147
1-582
1-269
1-222
-----
-----
Have the edges starting from the first line. Do not add any headers. The labels of nodes in the network should be numerical starting from 1 (not 0) and onwards to ensure proper processing. The singleton nodes appear in the file as just the node labels, one in a line. It is likely that the original file does not have such a format. The user must
first convert the original edge file into this format for using the algorithm. 

Steps:
1. Create a list of degree and "number of nodes" pair separated by comma. We can use "RawHistogramFromNetwork.py" for this. It creates a degree-frequency histogram. 
Input: "_pr.ed" file.
Output: ".csv" file.
Example lines of the output file:
0,19
1,95
2,36
-----
-----


2. Parameter file: This is a ".dat" file of the following structure.
Start of the file ---------------

@RangesStart
l:0.0,0.022885572139303482,0.045771144278606964,0.06865671641791045,0.09154228855721393,0.11442786069651742,0.1373134328358209,0.16019900497512438,0.18308457711442785,0.20597014925373133,0.22885572139303484,0.2517412935323383,0.2746268656716418,0.2975124378109453,0.32039800995024875,0.34427860696517415
u:0.022885572137014927,0.045771144274029854,0.06865671641104477,0.09154228854805971,0.11442786068507461,0.13731343282208955,0.1601990049591045,0.18308457709611942,0.2059701492331343,0.22885572137014923,0.2517412935071642,0.2746268656441791,0.2975124377811941,0.320398009918209,0.34427860693074624,1.0
@RangesEnd
n:51
nk:25.9,12.45,5.55,3.15,1.0,1.0,0.5,0.4,0.0,0.15,0.1,0.0,0.0,0.0,0.8,0.0
######### Ignore reading after this ############ Information only
bucket size=FD's (Freedman-Diaconis’s) rule, number of buckets=15+1 padding, delimiter in original file='-'

End of the file -------------------

Explanations:
@ comment lines
l: relative lower bounds
u: relative upper bounds
n: required number of nodes in the sample
nk: required number of nodes in the bin k.

Each line starts with one of these parameters. An empty bin is appended in the end (with 0 as the required number of nodes in it). This serves the purpose of closing the last bin at the place it closes in the original distribution.

We can use the python program "CreateNewParamsFile_FD_Rule.py" if Freedman-Diaconis’ rule is to be used for binning. It takes the histogram file as input. It ignores a header row that may have "node,degree". Otherwise, it reads the first line as a legitimate node-degree pair.
For "CreateNewParamsFile_FD_Rule.py",
Input: ".csv" file
Output: ".dat" file

Inside the python file, provide data_dir, data_file, and all_sample_sizes. 
For example:
data_dir = "My_DataFilesPy/"
# data_file = "email-Eu-core_Histogram.csv"
data_file = "musae_DE_Histogram.csv"
all_sample_sizes = [0.1, 0.2, 0.3]  # Fraction of the real size. 10%, 20%, 30%.


We can use any binning criteria, however, the user has to write a program for other binning rule ensuring the ".dat" file format is followed as shown above. 

3. The Arg file: A ".arg" file with lines like shown below. This file will be read by the sampling program.
../../DataFilesPy email-Eu-core-51N16B_FD.dat email-Eu-core_pr ../../Logs
Explanation: "parent directory of the files" "parameter file" "network file" "path for logs"

4. Keep "_pr.ed", ".dat", and ".csv" files in the same folder. The ".arg" file can reside in a different folder. Relative paths in the sampling program and the arg file may require adjustments.

5. Sampling program: The main heuristic file is "Net_Sampling_Heuristic.py". This file requires choosing the specific algorithm.
- Inside the program, adjust args_fname and set parameter "using_heuristic_type" to either BD or HyBND. Accordingly, the algorithm runs.
Input: ".arg" file
Output: sample file.

6. For very large networks (more than 150,000 nodes), use another algorithms (such as the one mentioned in the paper) to reduce the size to about 200,000. After that, use the Net_Sampling_Heuristic.py for the sampling.