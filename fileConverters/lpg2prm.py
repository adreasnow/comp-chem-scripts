#! python3

import sys

def ff2adj(xyzfile, keyfile, nameroot):

######### xyz #########
    xyzList = []
    with open(xyzfile, 'r') as f:
        lines = f.readlines()

    for line in lines:
        try:
            splitline = line.split()
            a, x, y, z, i, a1 = splitline[1:7]
            try: a2 = splitline[8]
            except: a2 = 0
            try: a3 = splitline[9]
            except: a3 = 0
            try: a4 = splitline[10]
            except: a4 = 0
            xyzList += [[a, float(x), float(y), float(z), int(i), int(a1), int(a2), int(a3), int(a4)]]
        except:
            pass

    for atom in xyzList:
        print(f'{atom[0]} {atom[1]:15f} {atom[2]:15f} {atom[3]:15f} {atom[4]:10d} {atom[5]:6d} {atom[6]:6d} {atom[7]:6d} {atom[8]:6d}')


######### prm conversion #########
    with open(keyfile, 'r') as f:
        lines = f.readlines()

    atomDict = {}
    vdwList = []
    bondList = []
    angleList = []
    ubList = []
    imptorsList = []
    torsionList = []

    for line in lines:
        try:
            splitLine = line.split()
            if splitLine[0] == 'atom':
                atomDict[splitLine[1]] = [splitLine[4]]
            elif splitLine[0] == 'vdw':
                vdwList += [line]
            elif splitLine[0] == 'bond':
                bondList += [line]
            elif splitLine[0] == 'angle':
                angleList += [line]
            elif splitLine[0] == 'ureybrad':
                ubList += [line]
            elif splitLine[0] == 'imptors':
                imptorsList += [line]
            elif splitLine[0] == 'torsion':
                torsionList += [line]
            elif splitLine[0] == 'charge':
                atomDict[splitLine[1]] += [float(splitLine[2])]
            elif splitLine[0] == 'radiusrule':
                radiusrule = splitLine[1]
            elif splitLine[0] == 'radiussize':
                radiussize = splitLine[1]
            elif splitLine[0] == 'epsilonrule':
                epsilonrule = splitLine[1]
            elif splitLine[0] == 'vdw-14-scale':
                vdw14scale = splitLine[1]
            elif splitLine[0] == 'chg-14-scale':
                chg14scale = splitLine[1]

        except:
            pass


    prmString  = f'RadiusRule              {radiusrule}\n'
    prmString += f'EpsilonRule             {epsilonrule}\n'
    prmString += f'RadiusSize              {radiussize}\n'
    prmString += f'ImptorType              TRIGONOMETRIC\n'
    prmString += f'vdw-14-scale            {vdw14scale}\n'
    prmString += f'chg-14-scale            {chg14scale}\n'
    prmString += f'torsion-scale           1.0\n'
    prmString += f'NAtom {len(atomDict)}\n'
    prmString += f'Nvdw {len(atomDict)}\n'



    for atom in atomDict:
        prmString += f'Atom        {int(atom):<12d} {atomDict[atom][1]:< 6.4f}         {int(atom):<15d}\n'
    for vdw in vdwList:
        prmString += vdw
    for bond in bondList:
        prmString += f'B{bond[1:]}'
    for angle in angleList:
        prmString += f'A{angle[1:]}'
    for torsion in torsionList:
        split = torsion.split()
        prmString += f'T{torsion[1:]}'
    for imptor in imptorsList:
        prmString += f'Improper{imptor[8:]}'
    for ub in ubList:
        split = ub.split()
        prmString += f'UreyBrad{ub[8:]}'



    with open(f'{nameroot}-qchem.prm', 'w+') as f:
        f.write(prmString)


for file in sys.argv[1:]:
    if file[-3:] == 'xyz':
        xyzfile = file
    if file[-3:] == 'key':
        keyfile = file

nameroot = xyzfile.split('.')[0]


ff2adj(xyzfile, keyfile, nameroot)