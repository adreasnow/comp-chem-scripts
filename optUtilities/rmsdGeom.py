#! python3

import numpy as np
import sys

def xyz2mat(infile):
    with open(infile, 'r') as f:
        lines = f.readlines()
    
    outarray = []
    for line in lines[2:]:
        splitline = line.split()
        outarray += [[float(splitline[1]), float(splitline[2]), float(splitline[3])]]
    return outarray

def rmsd(mat1, mat2):
    sumlist = []
    for i in range(len(mat1)):
        np1 = np.array(mat1[i])
        np2 = np.array(mat2[i])
        len1 = np.sqrt(np1.dot(np1))
        len2 = np.sqrt(np2.dot(np2))
        sumlist += [np.square(np.subtract(len1, len2))]
    
    return np.sqrt(np.divide(np.sum(sumlist),len(sumlist)))
        

def main():
    arr1 = xyz2mat(sys.argv[1])
    arr2 = xyz2mat(sys.argv[2])
    print(rmsd(arr1, arr2))


if __name__ == "__main__":
    main()
