#! python3
import matplotlib.pyplot as plt
import numpy as np
import argparse

def read_args() -> argparse.ArgumentParser.parse_args:
    parser = argparse.ArgumentParser(
        description=(
            "Script for plotting ORCA .spectrum files"
        )
    )
    parser.add_argument(
        "-a",
        "--absorbance",
        help="Absorbance spectrum file",
        nargs=1,
        required=False,
    )
    parser.add_argument(
        "-e",
        "--emission",
        help="Emission spectrum file",
        nargs=1,
        required=False,
    )
    parser.add_argument(
        "-E",
        "--energy",
        default=['nm'],
        help="Units of energy to plot ([nm]/ev/w)",
        nargs=1,
        required=False,
    )
    parser.add_argument(
        "-x",
        "--xrange",
        default=None,
        help="Range of x values to plot",
        nargs=2,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-n",
        "--normalise",
        default=True,
        help="Turn of scaling of intensities to be between 0-1",
        required=False,
        action="store_false"
    )
    parser.add_argument(
        "-t",
        "--total",
        default=False,
        help="Plot total energy",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "--ht",
        default=False,
        help="Plot Herzberg-Teller contribution",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "--fc",
        default=False,
        help="Plot Franck-Condon contribution",
        required=False,
        action="store_true"
    )

    return parser.parse_args()

def readSpectrum(infile:str, energyUnits:str, norm:bool) -> dict[float]:
    energy = []
    total = []
    fc = []
    ht = []
    with open(infile, "r") as f:
        lines = f.readlines()
    for line in lines[1:]:
        vals = line.split()
        energy += [float(vals[0])]
        total += [float(vals[1])]
        fc += [float(vals[2])]
        ht += [float(vals[3])]
    if energyUnits == 'nm':
        energy = np.multiply(np.divide(1, energy), 1e7)
    if energyUnits == 'ev':
        energy = np.divide(1.23984198e-6, np.divide(np.divide(1, energy), 100))
    if energyUnits == 'w':
        energy = np.array(energy)

    returnDict = {'e': energy, 't': total, 'fc': fc, 'ht': ht}

    if norm == True:
        for i in ['t', 'fc', 'ht']:
            returnDict[i] = np.divide(returnDict[i], np.max(np.abs(returnDict[i])))

    return returnDict
        

def plot(dicts:dict, eList:list[float], energyUnits:str, xrange:list[int], figW:int=12, figH:int=5) -> plt.show:
    plotList = []
    for inDictList in dicts:
        eToPlot = []
        eToPlot += [['t', 'Total']] if eList[0] == True else []
        eToPlot += [['ht', 'Herzberg-Teller']] if eList[1] == True else []
        eToPlot += [['fc', 'Franck-Condon']] if eList[2] == True else []
        for i in eToPlot:
            plotList += [[inDictList[1]['e'], inDictList[1][i[0]], i[1], inDictList[0]]]
    
    

    fig, ax = plt.subplots(1,1, figsize=(figW,figH))
    for i in plotList:
        ax.plot(i[0], i[1], label=f'{i[3]} - {i[2]}')

    
    ax.set_ylabel(r'Intensity')
    ax.set_xlim((xrange[0], xrange[1]))
    plotUnits = r'$eV$' if energyUnits == 'ev' else r'$nm$' if energyUnits == 'nm' else r'$cm^{-1}$'
    ax.set_xlabel(f'Energy ({plotUnits})')
    ax.legend()
    return plt.show()


def main() -> NoReturn:
    args = read_args()
    dicts = []
    if args.absorbance == None and args.emission == None:
        print("No files specified, exiting.")
        exit()

    if args.xrange == None:
        xrange = [3.26, 1.77] if args.energy[0] == 'ev'\
            else [380, 700]   if args.energy[0] == 'nm'\
            else [26315, 14286]
    else:
        xrange = args.xrange

    if args.total == False and args.ht == False and args.fc == False:
        plotTotal = True
    else:
        plotTotal = args.total

    if args.absorbance != None:
        absorbDict = readSpectrum(args.absorbance[0], args.energy[0], args.normalise)
        dicts += [['Absorbance', absorbDict]]

    if args.emission != None:
        fluorDict = readSpectrum(args.emission[0], args.energy[0], args.normalise)
        dicts += [['Emission', fluorDict]]
    
    plot(dicts, [plotTotal, args.ht, args.fc], args.energy[0], xrange)

if __name__ == "__main__":
    main()