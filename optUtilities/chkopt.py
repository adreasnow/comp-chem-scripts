#!python3
import matplotlib.pyplot as plt
import argparse

def read_args():
    parser = argparse.ArgumentParser(
        description=(
            ""
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
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()

def nmToEv(nm):
    h = 4.135667e-15
    c = 2.99792e8
    eV = (h*c)/(nm*1e-9)
    return eV

def identifyProg(file, args):
    prog = ''
    root = args.root[0]
    with open(infile, "r") as file:
        lines = file.readlines()

    for line in lines:
        if "Welcome to Q-Chem" in line:
            print("Q-Chem")
            prog = 'qchem'
        elif "* O   R   C   A *" in line:
            print("ORCA")
            prog = 'orca'
        elif "Psi4" in line:
            print("Psi4")
            prog = 'psi4'
        elif "This is part of the Gaussian(R)" in line:
            print("Gaussian")
            prog = 'gaussian'
        elif " x T B" in line:
            print('XTB')
            prog = 'xtb'
        elif prog == 'qchem' and 'cis_state_deriv' in line.lower() and root == 0:
            root = line.split()[1]
        
    return prog, lines, root

def extractTransition(prog, lines, root):
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
        print('Psi4 transitions not implemnted')
        exit()
    elif prog == 'xtb':
        print('XTB transitions not implemnted')
        exit()
    return [],  y

def extractProgress(prog, lines):
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

    elif prog == 'xtb':
        for count, line in enumerate(lines):
            lineCount = 4
            if '* total energy  :' in line:
                for i in range(lineCount):
                    outString += [lines[count+i]]
                outString += ['--']
        for i in outString[-((lineCount*2)+3):]:
            print(i.strip('\n'))
    return

def extractEnergy(prog, lines, args, root):
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

    elif prog == 'xtb':
        for line in lines:
            if 'total energy  :' in line:
                y += [float(line.split()[4])]
    return [],  y


args = read_args()
labelname = []

if args.progress == False:
    plot = True
    fig = plt.figure(figsize=(12,5))
else:
    plot = False


for infile in args.files:
    prog, lines, root = identifyProg(infile, args)

    if args.transition == True:
        x, y = extractTransition(prog, lines, root)
        x = []

    elif args.progress == True:
        extractProgress(prog, lines)
        
    else: 
        x, y = extractEnergy(prog, lines, args, root)


    if plot == True:        
        ax = fig.add_subplot(111)
        if args.transition == True: ax.set_ylabel("Excitation Energy (eV)")
        else: ax.set_ylabel("Energy (Eh)")
        ax.set_xlabel("OPT Iteration")


        fig.gca().ticklabel_format(axis='both', style='plain', useOffset=False)

        for i in range(len(y)):
            y[i] = float(y[i])

        for i in range(len(y)):
            x.append(i)

        ax.plot(x, y, '.-')
        labelname += [str(str(infile.split("/")[-1].split(".")[0]))]

if plot == True:    
    if root != 0: print(f'Root = {root}')
    ax.legend(labelname)
    plt.show()