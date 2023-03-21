#!python3
import argparse
import numpy as np
from tabulate import tabulate
from pathlib import Path
from enum import Enum

def read_args() -> argparse.ArgumentParser.parse_args:
    parser = argparse.ArgumentParser(
        description=(
            ""
        )
    )
    parser.add_argument(
        "-r",
        "--rows",
        help="Number of rows to display in the table",
        nargs=1,
        default=15,
        type=int,
        required=False,
    )
    parser.add_argument(
        "-i",
        "--ie",
        help="Initial state energy if not supplied in hessian",
        nargs=1,
        default=0.0,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-f",
        "--fe",
        help="Final state energy if not supplied in hessian",
        nargs=1,
        default=0.0,
        type=float,
        required=False,
    )
    parser.add_argument(
        'files', 
        type=Path,
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()

class Which(Enum):
    init = 'init'
    final = 'final'

class Program(Enum):
    orca = 'orca'
    qchem = 'qchem'
    none = 'None'


def zpve(freq: np.array) -> float:
    c = 2.9979e8
    h = 6.6260e-34
    return (np.sum(np.multiply(np.multiply(np.multiply(freq, c), 100), h)) / 2) * 2.294e17

def zz(init_zpve: float, init_e: float, final_zpve: float, final_e:float) -> float:
    return (final_zpve + final_e) - (init_zpve + init_e)
 
def transitions(init_freqs: np.array, init_e: float, final_freqs: np.array, final_e:float) -> np.array:
    c = 2.9979e8
    h = 6.6260e-34
    init_zpve = zpve(init_freqs)
    final_zpve = zpve(final_freqs)
    zz_e = zz(init_zpve, init_e, final_zpve, final_e) * 27.2114

    energies = np.multiply(np.multiply(np.multiply(np.multiply(final_freqs, c), 100), h), 27.2114 * 2.294e17)
    outEnergies = np.add(energies, zz_e)
    return outEnergies


def readHess(file:Path, args, which: Which) -> tuple[float, float, np.array]:
    print('Treating as ORCA hessian file')
    with open(file, 'r') as f:
        lines = f.readlines()

    eLine = 0
    vLine = 0
    for count, line in enumerate(lines):
        if '$act_energy' in line:
            eLine = count + 1
        elif '$vibrational_frequencies' in line:
            vLine = count + 1
    
    if eLine == 0  or vLine == 0:
        print(f'Hessian file {file} could not be read')
        exit()

    eOut = float(lines[eLine])

    if which == Which.init and args.ie != 0.0:
        eOut = args.ie
    elif which == Which.final and args.fe != 0.0:
        eOut = args.fe
    elif eOut == 0.0 and ((which == Which.init and args.ie == 0.0) or (which == Which.final and args.fe == 0.0)):
        print(f'Hessian {file.stem} does not contain energy and none was supplied in the arguments')
        exit()

    vCount = int(lines[vLine])

    freqs = np.array([0.0])
    for line in lines[vLine+1:vLine+vCount+1]:
        freq = float(line.split()[1])
        if freq != 0.0:
            freqs = np.append(freqs, freq)

    return eOut, zpve(np.array(freqs)), freqs

def readOut(file:Path, args, which: Which) -> tuple[float, float, np.array]:
    prog = Program.none
    with open(file, 'r') as f:
        for line in f.readlines():
            if '* O   R   C   A *' in line:
                prog = Program.orca
                break
            if 'Q-Chem, Inc., Pleasanton, CA' in line:
                prog = Program.qchem
                break
    if prog == Program.orca:
        print('Treating as ORCA output file')
        return readORCA(file, args, which)
    if prog == Program.qchem:
        print('Treating as QChem output file')
        return readQChem(file, args, which)
    else:
        print('Program not recognised')
        exit()

def readORCA(file:Path, args, which: Which) -> tuple[float, float, np.array]:
    with open(file, 'r') as f:
        lines = f.readlines()

    eOut = 0.0
    vLine = 0
    for count, line in enumerate(lines):
        if 'FINAL SINGLE POINT ENERGY' in line:
            eOut = float(line.split()[4])
        elif 'VIBRATIONAL FREQUENCIES' in line:
            vLine = count + 5
    
    if eOut == 0.0  and vLine == 0:
        print(f'ORCA output file {file} could not be read')
        exit()

    if which == Which.init and args.ie != 0.0:
        eOut = args.ie
    elif which == Which.final and args.fe != 0.0:
        eOut = args.fe

    freqs = np.array([0.0])
    for line in lines[vLine:]:
        try:
            freq = float(line.split()[1])
            if freq != 0.0:
                freqs = np.append(freqs, freq)
        except IndexError:
            break
    return eOut, zpve(np.array(freqs)), freqs

def readQChem(file:Path, args, which: Which) -> tuple[float, float, np.array]:
    with open(file, 'r') as f:
        lines = f.readlines()

    eStartLine = 0
    eEndLine = 0
    eOut = 0.0
    vLine = 0
    for count, line in enumerate(lines):
        if 'Desired analytical derivatives not available' in line:
            eStartLine = count
        elif ' # Starting finite difference calculation #' in line:
            eEndLine = count
        elif 'VIBRATIONAL ANALYSIS' in line:
            vLine = count + 10

    for line in lines[eStartLine:eEndLine]:
        if 'Total energy in the final basis set =' in line:
            eOut = float(line.split()[8])
    
    if eOut == 0.0  and vLine == 0:
        print(f'QChem output file {file} could not be read')
        exit()

    if which == Which.init and args.ie != 0.0:
        eOut = args.ie
    elif which == Which.final and args.fe != 0.0:
        eOut = args.fe

    freqs = np.array([0.0])
    for line in lines[vLine:]:
        if 'Frequency:' in line:
            splitline = line.split()[1:]
            for freqStr in splitline:
                freq = float(freqStr)
                if freq != 0.0:
                    freqs = np.append(freqs, freq)
        if 'STANDARD THERMODYNAMIC QUANTITIES' in line:
            break

    return eOut, zpve(np.array(freqs)), freqs

def buildTable(vtList: np.array, rows: int) -> str:
    names = []
    for i in range(len(vtList)):
        names += [f'0-{i}']
    tableDict = {}
    align = ()
    headers = []
    count = 1
    for i in range(0, len(vtList), rows):
        tableDict[f'T-{count}'] = names[i:i+rows] 
        tableDict[f'ΔE(eV)-{count}'] = vtList[i:i+rows] 
        align += ("right", "left")
        headers += ['T', 'ΔE (eV)']
        count += 1

    
    return tabulate(tableDict, headers=headers, floatfmt=(".3f"), colalign=align)

def main() -> None:
    args = read_args()

    if len(args.files) != 2:
        print('Exactly two files need to be imported')
        exit()
    (init_file, final_file) = args.files
    if init_file.suffix == '.hess':
        init_e, init_zpve, init_freq = readHess(init_file, args, Which.init)
        final_e, final_zpve, final_freq = readHess(final_file, args, Which.final)
    elif init_file.suffix == '.out':
        init_e, init_zpve, init_freq = readOut(init_file, args, Which.init)
        final_e, final_zpve, final_freq = readOut(final_file, args, Which.final)
    else:
        print(f'File type {init_file.suffix} not supported')
    vtList = transitions(init_freq, init_e, final_freq, final_e)

    print(buildTable(vtList, args.rows))

if __name__ == "__main__":
    main()