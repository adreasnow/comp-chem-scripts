#!python3
import matplotlib.pyplot as plt
import argparse
from time import sleep

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Chek optimisation progress for Q-Chem, Gaussian, Psi4 and ORCA files. Allows for plotting tddft transiiton energy, system energy, or printing the optimisation progress"
        )
    )
    parser.add_argument(
        "-r",
        "--root",
        help='Root to follow. If plotting the energy, this will force it to look for the energy of the specific root.',
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--transition",
        help='Plot transition energy',
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-p",
        "--progress",
        help='Print job progress',
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-w",
        "--watch",
        help='"Watch" the file/s (refresh every 30 seconds unless overridden with -i)',
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-i",
        "--interval",
        help='If using -w, this specifies the interval to refresh',
        nargs=1,
        default=[30],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-l",
        "--last",
        help='Only plots the last n steps',
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()

def nmToEv(nm:float) -> float:
    h = 4.135667e-15
    c = 2.99792e8
    eV = (h*c)/(nm*1e-9)
    return eV

def identifyProg(infile:str, args:argparse.Namespace) -> tuple[str, list[str], int]:
    global printed
    prog = ''
    root = args.root[0]
    with open(infile, "r") as file:
        lines = file.readlines()

    for line in lines:
        if "Welcome to Q-Chem" in line:
            if printed == False: print("Q-Chem")
            prog = 'qchem'
        elif "* O   R   C   A *" in line:
            if printed == False: print("ORCA")
            prog = 'orca'
        elif "Psi4" in line:
            if printed == False: print("Psi4")
            prog = 'psi4'
        elif "This is part of the Gaussian(R)" in line:
            if printed == False: print("Gaussian")
            prog = 'gaussian'
        elif " x T B" in line:
            if printed == False: print('XTB')
            prog = 'xtb'
        elif 'Northwest Computational Chemistry Package' in line:
            if printed == False:print('NWChem')
            prog = 'nwchem'
        elif 'pyscf.' in line:
            if printed == False:print('PySCF')
            prog = 'pyscf'
            printed = True

        # Root detection
        elif prog == 'psi4' and 'follow_root' in line.lower() and root == 0:
            root = line.split()[1]
        elif prog == 'qchem' and 'cis_state_deriv' in line.lower() and root == 0:
            root = line.split()[1]
        elif prog == 'prog' and 'root' in line.lower() and root == 0:
            root = line.split()[1]
        
    return prog, lines, root

def extractTransition(prog:str, lines:list[str], root:int) -> tuple[list[float], list[float]]:
    if root == 0: root = 1
    y = []
    
    if prog == 'orca':
        for count, line in enumerate(lines):
            if 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' in line:
                y += [nmToEv(float(lines[count+4+root].split()[2]))]

    elif prog == 'qchem':
        for line in lines:
            if f'{root}: excitation energy (eV) =' in line:
                y += [float(line.split()[7])]
    elif prog == 'gaussian':
        print('Gaussian transitions not implemnted')
        exit()
    elif prog == 'psi4':
        for line in lines:
            if f'EOM State {root}' in line:
                y += [float(line.split()[3])]
    elif prog == 'xtb':
        print('XTB transitions not implemnted')
        exit()
    elif prog == 'nwchem':
        mwchemTransition = False
        for line in lines:
            if f'Root   {root} singlet ' in line:
                if mwchemTransition == True:
                    y += [float(line.split()[6])]
                    mwchemTransition = False
                else:
                    mwchemTransition = True
    elif prog == 'pyscf':
        print('PySCF transitions not implemnted')
        exit()

    x = []
    for i in range(len(y)): x += [i]
    return x,  y

def extractProgress(prog:str, lines:list[str]) -> None:
    outString = []
    if prog == 'orca':
        for count, line in enumerate(lines):
            lineCount = 7
            if 'Geometry convergence' in line:
                for i in range(lineCount):
                    outString += [lines[count+i]]
                outString += ['--']
        for i in outString[-((lineCount*2)+3):]:
            print(i.strip('\n'))

    elif prog == 'qchem':
        for count, line in enumerate(lines):
            lineCount = 4
            if 'Maximum     Tolerance    Cnvgd?' in line:
                for i in range(lineCount):
                    outString += [lines[count+i]]
                outString += ['--']
            elif 'LBFGS Step' in line:
                outString += [line]
                outString += ['--']
        for i in outString[-((lineCount*2)+3):]:
            print(i.strip('\n'))
    elif prog == 'gaussian':
        for count, line in enumerate(lines):
            lineCount = 5
            if 'Converged' in line:
                for i in range(lineCount):
                    outString += [lines[count+i]]
                outString += ['--']
        for i in outString[-((lineCount*2)+3):]:
            print(i.strip('\n'))

    elif prog == 'psi4':
        for line in lines:
            if '~' in line:
                print(line)

    elif prog == 'nwchem':
        for line in lines:
            if '@' in line:
                print(line)

    elif prog == 'xtb':
        for count, line in enumerate(lines):
            lineCount = 4
            if '* total energy  :' in line:
                for i in range(lineCount):
                    outString += [lines[count+i]]
                outString += ['--']
        for i in outString[-((lineCount*2)+3):]:
            print(i.strip('\n'))

    elif prog == 'pyscf':
        for count, line in enumerate(lines):
            if 'norm(grad) =' in line:
                print(line)
    return

def extractEnergy(prog:str, lines:list[str], root:int) -> tuple[list[float], list[float]]:
    y = []
    if prog == 'orca':
        for line in lines:
            if 'FINAL SINGLE POINT ENERGY' in line:
                y += [float(line.split()[4])]

    elif prog == 'qchem':
        for line in lines:
            if f'Total energy in the final basis set = ' in line and root == 0:
                y += [float(line.split()[8])]
            elif f'Total energy for state  {root}:' in line and root != 0:
                y += [float(line.split()[5])]
    elif prog == 'gaussian':
        for line in lines:
            if ' SCF Done:' in line:
                y += [float(line.split()[4])]

    elif prog == 'psi4':
        for line in lines:
            if 'Total Energy = ' in line:
                y += [float(line.split()[3])]

    elif prog == 'nwchem':
        for line in lines:
            if '@' in line:
                try:
                    newY = float(line.split()[2])
                    y += [newY]
                except:
                    pass

    elif prog == 'xtb':
        for line in lines:
            if 'total energy  :' in line:
                y += [float(line.split()[4])]

    elif prog == 'pyscf':
        for line in lines:
            if 'norm(grad) =' in line:
                y += [float(line.split()[4])]
    x = []
    for i in range(len(y)): x += [i]
    return x,  y

def plotFunc(infile:str, args:argparse.Namespace, fig:plt.figure, ax: plt.Axes) -> None:
    global printed
    global labelname

    label = str(str(infile.split("/")[-1].split(".")[0]))
    if printed == False: print(label)
    prog, lines, root = identifyProg(infile, args)

    if args.transition == True: x, y = extractTransition(prog, lines, root)
    else:                       x, y = extractEnergy(prog, lines, root)


    
    
    ax.set_xlabel("OPT Iteration")
    if args.transition == True: ax.set_ylabel("Excitation Energy (eV)")
    else:                       ax.set_ylabel("Energy (Eh)")

    fig.gca().ticklabel_format(axis='both', style='plain', useOffset=False)

    if args.last[0] == 0:
        ax.plot(x, y, '.-')
    else:
        try:
            plotLen = len(x) if len(x) < args.last[0] else args.last[0]
            y = y[-plotLen:]
            x = list(range(plotLen))
            ax.plot(x, y, '.-')
        except Exception as e:
            print(f'Problem with {label}:')
            print(e)

    labelname += [label]

    if root != 0 and printed == False: print(f'Root = {root}')

    ax.legend(labelname)
    plt.draw()
    return

def main():
    args = read_args()

    global labelname
    global printed
    labelname = []
    printed = False

    if args.progress == True:
        if args.watch == True:
            while True:
                for infile in args.files:
                    label = str(str(infile.split("/")[-1].split(".")[0]))
                    if printed == False: print(label)
                    prog, lines, root = identifyProg(infile, args)
                    extractProgress(prog, lines)
                printed = True
                sleep(args.interval[0])
        else:
            for infile in args.files:
                prog, lines, root = identifyProg(infile, args)
                extractProgress(prog, lines)
            exit()

    fig = plt.figure(figsize=(12,5))

    if args.watch == True: 
        while True:
            ax = fig.add_subplot(111)
            for infile in args.files:
                plotFunc(infile, args, fig, ax)
            printed = True
            plt.pause(args.interval[0])
            plt.clf()  
    else:
        ax = fig.add_subplot(111)
        for infile in args.files:
            plotFunc(infile, args, fig, ax)
        plt.show()

if __name__ == "__main__":
    main()