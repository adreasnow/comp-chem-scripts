#!python3
import argparse
import numpy as np
from tabulate import tabulate
from pathlib import Path

def read_args() -> argparse.ArgumentParser.parse_args:
    parser = argparse.ArgumentParser(
        description=(
            ""
        )
    )
    parser.add_argument(
        "-g",
        "--ge",
        help="Ground state energy if not supplied in hessian",
        nargs=1,
        default=0.0,
        type=float,
        required=False,
    )
    parser.add_argument(
        "-e",
        "--ee",
        help="Ground state energy if not supplied in hessian",
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


def readHess(file:Path, args) -> tuple[float, float, np.array]:
    with open(file, 'r') as f:
        lines = f.readlines()

    eLine = 0
    vLine = 0
    for count, line in enumerate(lines):
        if '$act_energy' in line:
            eLine = count + 1
        elif '$vibrational_frequencies' in line:
            vLine = count + 1
    
    if eLine == 0  and vLine == 0:
        print(f'Hessian file {file} could not be read')
        exit()

    eOut = float(lines[eLine])
    if eOut == 0.0 and args.ge == 0.0:
        print(f'Hessian {file.stem} does not contain energy and none was supplied in the arguments')
        exit()

    vCount = int(lines[vLine])

    freqs = np.array([0.0])
    for line in lines[vLine+1:vLine+vCount+1]:
        freq = float(line.split()[1])
        if freq != 0.0:
            freqs = np.append(freqs, freq)

    return eOut, zpve(np.array(freqs)), freqs

def buildTable(vtList) -> str:
    names = []
    for i in range(len(vtList)):
        names += [f'0-{i}']
    return tabulate({'Transition': names,
                     'Energy (eV)': vtList
                     },
                     headers="keys",
                     floatfmt=(".3f"),
                     colalign=("right", "left"))

    
def main() -> None:
    args = read_args()

    if len(args.files) != 2:
        print('Exactly two files need to be imported')
        exit()
    (init_file, final_file) = args.files
    if init_file.suffix == '.hess':
        init_e, init_zpve, init_freq = readHess(init_file, args)
        final_e, final_zpve, final_freq = readHess(final_file, args)
    else:
        print(f'File type {init_file.suffix} not supported')
    vtList = transitions(init_freq, init_e, final_freq, final_e)

    print(buildTable(vtList))

if __name__ == "__main__":
    main()