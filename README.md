[![INFORMS Journal on Computing Logo](https://INFORMSJoC.github.io/logos/INFORMS_Journal_on_Computing_Header.jpg)](https://pubsonline.informs.org/journal/ijoc)

# Degree Distribution Preserving Network Sampling: The Case of Relational Learning

This archive is distributed in association with the [INFORMS Journal on
Computing](https://pubsonline.informs.org/journal/ijoc) under the [MIT License](LICENSE).

The software and data in this repository are a snapshot of the software and data
that were used in the research reported on in the paper 
[Degree Distribution Preserving Network Sampling: The Case of Relational Learning](https://doi.org/10.1287/ijoc.2024.1002) by A. Ghoshal, S. Menon, and S. Sarkar. 
The snapshot is based on [this SHA](https://github.com/abhi-public/2024.1002) 
in the development repository. 


## Cite

To cite the contents of this repository, please cite both the paper and this repo, using their respective DOIs.

https://doi.org/10.1287/ijoc.2024.1002

https://doi.org/10.1287/ijoc.2024.1002.cd

Below is the BibTex for citing this snapshot of the repository.

```
@misc{NetSampling2025,
  author =        {A. Ghoshal, S. Menon, S. Sarkar},
  publisher =     {INFORMS Journal on Computing},
  title =         {Degree Distribution Preserving Network Sampling: The Case of Relational Learning},
  year =          {2025},
  doi =           {10.1287/ijoc.2024.1002.cd},
  url =           {https://github.com/INFORMSJoC/2024.1002},
  note =          {Available for download at https://github.com/INFORMSJoC/2024.1002},
}  
```

## Description

The goal of this software is to generate a sample of a network whose degree distribution is similar to that of the original network.

## Running the Heuristic

The code is written in python 3.8 version. The code does not require any building and can be run using the command 

```
python Net_Sampling_Heuristic.py
```

All python files are written using packages downloaded from Anaconda Distribution.

To use the heuristic, follow the instructions in the file [ReadMe-StepsForRunningTheHeuristic.txt](https://github.com/abhi-public/2024.1002/blob/main/FinalPrograms/ReadMe-StepsForRunningTheHeuristic.txt).
  
## Replicating

The default imlementation replicates the results for dataset 'musae_DE_pr.dat'.


```

## Ongoing Development

This code is being developed on an on-going basis at the author's
[Github site](https://github.com/abhi-public).

## Support

For support in using this software, submit an
[issue](https://github.com/abhi-public/2024.1002/issues/new).
