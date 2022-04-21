#! python3
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import numpy as np
import sys

try:
    infile = sys.argv[1]
except:
    print('ORCA outpput file not provided.\nExiting...')
    exit()


def readORCAOrbs(infile):
    with open(infile, "r") as f:
        lines = f.readlines()
    mark = []
    orbitals = []
    labels = []
    occupation = []
    for i, val in enumerate(lines):
        if "ORBITAL ENERGIES" in val:
            mark += [i+4] 
    for j in range(mark[-1], mark[-1]+9999):
        line = lines[j].split()
        try:
            orbitals += [float(line[3])]
            labels += [int(line[0])]
            occupation += [float(line[1])]
        except:
            break
        
    occupationCol = np.divide(np.add(np.multiply(np.divide(occupation, 2), 120), 240), 360)

    occupationColOut = []
    for i, val in enumerate(occupationCol):
        r, g, b = hsv_to_rgb((val, 1, 1))
        occupationColOut += [(r, g, b)]
    return(orbitals, labels, occupationColOut, occupation)


def makeDegeneracyList(orbitals, degeneracyTol):
    currentBin = []
    bins = []
    binNum = 0
    maxDegeneracy = 0
    for i in range(len(orbitals)):
        if i == 0:
            currentBin += [binNum] # set our intial bin number
            binNum += 1
        else:
            if abs(orbitals[i] - orbitals[i-1]) <= degeneracyTol: # if the energy difference between this and the previous orbital is
                currentBin += [binNum] #                             witihin the degenracy tolerance, append to the current bin
                binNum += 1
            else:
                bins += [currentBin]              # otherwise, append the previous bin to the bin list 
                binNum = 0
                currentBin = [binNum]             # create a new bin with the new bin number
                binNum += 1
                if len(bins[-1]) > maxDegeneracy: # update the max bin size
                    maxDegeneracy = len(bins[-1])
    bins += [currentBin]

    if len(bins[-1]) > maxDegeneracy:             # in case the last bin was degenerate, we want to update the bin size anyway
        maxDegeneracy = len(bins[-1])

    offsetBins = []
    for i in bins:
        if len(i)%2 != 0:
            if len(i) != 1:
                newbin = np.subtract(i, (len(i)-1)/2)
            else:
                newbin = i
        else:
            newbin = np.subtract(i, (len(i)-1)/2)
            
        offsetBins = np.append(offsetBins, newbin)
    return offsetBins

def plot(degeneracyTol=0.05, ymax=10, ymin=-20, annotateSize=6, annotateOffset=0.5, figH=10, figW=5):
    fig, ax = plt.subplots(1,1, figsize=(figW,figH))

    try:
        orbitals, labels, occupationCol, occupation = readORCAOrbs(infile)
    except:
        print(f'Error reading orca input file:\n"{infile}"\nExiting...')
        exit()

    degen = makeDegeneracyList(orbitals, degeneracyTol)

    ax.scatter(degen, orbitals, marker='_', s=2000, color=occupationCol)

    for i, val in enumerate(labels):
        ax.annotate(val, (degen[i]+annotateOffset, orbitals[i]), fontsize=annotateSize)
    for i, val in enumerate(occupation):
        if val < 1.999 and val > 0.001:
            ax.annotate(val, (degen[i]-annotateOffset*2, orbitals[i]), fontsize=annotateSize)

    ax.set_ylim((ymin, ymax))
    ax.set_xlim((min(degen-0.5), max(degen+0.5)))
    ax.set_ylabel(r'Energy ($eV$)')
    ax.set_xticks([], [])
    plt.show()

plot()