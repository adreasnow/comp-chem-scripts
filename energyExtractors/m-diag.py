#! python3
import numpy as np
import argparse
from aenum import Enum, auto

class prog(Enum):
    orca = auto()
    qchem = auto()
    nwchem = auto()
    gaussian = auto()
    pyscf = auto()
    psi4 = auto()

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            ""
        )
    )
    parser.add_argument(
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()

def identify_prog(lines:list[str]) -> prog:
    global printed
    for line in lines:
        if "Welcome to Q-Chem" in line:
            print('Q-Chem not implemented')
            exit()
            return prog.qchem
        elif "* O   R   C   A *" in line:
            return prog.orca
        elif "Psi4" in line:
            print('Psi4 not implemented')
            exit()
            return prog.psi4
        elif "This is part of the Gaussian(R)" in line:
            print('Gaussian not implemented')
            exit()
            return prog.gaussian
        elif 'Northwest Computational Chemistry Package' in line:
            print('NWChem not implemented')
            exit()
            return prog.nwchem
    raise Exception("Program not identified")

def extract_electrons(lines:list[str], program:prog) -> int:
    if program == prog.orca:
        for line in lines:
            if 'Total number of electrons' in line:
                return int(line.split()[5])

def extract_occ(lines:list[str], program:prog) -> list[float]:
    if program == prog.orca:
        for count, line in enumerate(lines):
            if '  NO   OCC          E(Eh)            E(eV) ' in line:
                start = count+1
                occs = []
                for orbs in lines[start:]:
                    try:
                        occs += [float(orbs.split()[1])]
                    except IndexError:
                        break
    return occs

def build_ref(electrons:int, occ:list[float]) -> list[float]:
    ref = []
    while electrons > 0:
        if electrons >= 2:
            ref += [2.]
            electrons -= 2
        else:
            ref += [1.]
            electrons -= 1
    for i in range(len(occ)-len(ref)):
        ref += [0.]
    return ref

def m_diag(occ_ref:list[float]|np.ndarray, occ_no:list[float]|np.ndarray) -> float:
    if type(occ_ref) == list: occ_ref = np.array(occ_ref)
    if type(occ_no) == list: occ_no = np.array(occ_no)

    docc = occ_no[np.equal(occ_ref, 2.)].tolist()
    socc = occ_no[np.equal(occ_ref, 1.)].tolist()
    uocc = occ_no[np.equal(occ_ref, 0.)].tolist()
    soccm1 = np.abs(np.subtract(socc, 1))
    m = 0.5*(2-min(docc)+np.sum(soccm1)+max(uocc))
    return round(m, 3)

def main() -> None:
    args = read_args()
    for file in args.files:
        with open(file, "r") as file:
            lines = file.readlines()
        program = identify_prog(lines)
        electrons = extract_electrons(lines, program)
        occ = extract_occ(lines, program)
        ref = build_ref(electrons, occ)
        m = m_diag(ref, occ)
        print(m)

if __name__ == "__main__":
    main()