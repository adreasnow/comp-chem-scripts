#! python3
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import numpy as np
import sys
import argparse

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reads orbitals from ORCA and plots them with support for multiconfiguration"
        )
    )
    parser.add_argument(
        "-d",
        "--degeneracy",
        help='Tolerance to group degeneratre orbitals',
        default=0.05,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-s",
        "--size",
        help='Annotation size',
        default=6,
        type=int,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--offset",
        help='Annotation offset',
        default=0.5,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-f",
        "--fig",
        help='Figure dimensions as \"H W\"',
        default=[10, 5],
        nargs=2,
        type=int,
        required=False,
    )
    parser.add_argument(
        "-y",
        "--ylim",
        help='Limits of the Y axis as \"min max\"',
        default=[-20, 10],
        nargs=2,
        type=int,
        required=False,
    )

    parser.add_argument(
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()


def readORCAOrbs(infile:str) -> tuple[list[float], list[int], list[float], list[float]]:
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


def makeDegeneracyList(orbitals:list[float], degeneracyTol:float) -> list[int]:
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

def plot(infile:str, args:argparse.Namespace):
    degeneracyTol = args.degeneracy
    figH, figW = args.fig
    ymin, ymax = args.ylim
    annotateSize = args.size
    annotateOffset = args.offset

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
            if val >= 1.95 or val <=0.05:
                ax.annotate(val, (degen[i]-annotateOffset*2, orbitals[i]), fontsize=annotateSize, weight='bold', bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="magenta", lw=2))
            else:
                ax.annotate(val, (degen[i]-annotateOffset*2, orbitals[i]), fontsize=annotateSize, weight='bold', bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="green", lw=2))

    ax.set_ylim((ymin, ymax))
    ax.set_xlim((min(degen-0.5), max(degen+0.5)))
    ax.set_ylabel(r'Energy ($eV$)')
    ax.set_xticks([], [])
    plt.show()

def main():
    args = read_args()
    for file in args.files:
        plot(file, args)

if __name__ == "__main__":
    main()