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
            elif splitLine[0] == 'vdwindex':
                vdwindex = splitLine[1]
            elif splitLine[0] == 'vdwtype':
                vdwtype = splitLine[1]
            elif splitLine[0] == 'radiusrule':
                radiusrule = splitLine[1]
            elif splitLine[0] == 'radiustype':
                radiustype = splitLine[1]
            elif splitLine[0] == 'radiussize':
                radiussize = splitLine[1]
            elif splitLine[0] == 'epsilonrule':
                epsilonrule = splitLine[1]
            elif splitLine[0] == 'torsionunit':
                torsionunit = splitLine[1]
            elif splitLine[0] == 'imptorunit':
                imptorunit = splitLine[1]
            elif splitLine[0] == 'vdw-14-scale':
                vdw14scale = splitLine[1]
            elif splitLine[0] == 'chg-14-scale':
                chg14scale = splitLine[1]
            elif splitLine[0] == 'electric':
                electric = splitLine[1]
            elif splitLine[0] == 'dielectric':
                dielectric = splitLine[1]
            elif splitLine[0] == 'forcefield':
                forcefield = splitLine[1]
        except:
            pass


    prmString = '''


      ##############################
      ##                          ##
      ##  Force Field Definition  ##
      ##                          ##
      ##############################

'''
    prmString += f'forcefield              {forcefield}\n\n'

    prmString += f'vdwindex                {vdwindex}\n'
    prmString += f'vdwtype                 {vdwtype}\n'
    prmString += f'radiusrule              {radiusrule}\n'
    prmString += f'radiustype              {radiustype}\n'
    prmString += f'radiussize              {radiussize}\n'
    prmString += f'epsilonrule             {epsilonrule}\n'
    prmString += f'imptortype              HARMONIC\n'
    prmString += f'torsionunit             {torsionunit}\n'
    prmString += f'imptorunit              {imptorunit}\n'
    prmString += f'vdw-14-scale            {vdw14scale}\n'
    prmString += f'chg-14-scale            {chg14scale}\n'
    prmString += f'electric                {electric}\n'
    prmString += f'dielectric              {dielectric}\n\n'
    prmString += f'natom {len(atomDict)}\n'
    prmString += f'nvdw {len(atomDict)}\n\n'



    for atom in atomDict:
        prmString += f'atom     {atom}    {atomDict[atom][1]:10f}     {atom}     {atomDict[atom][0]}\n'
    prmString += '\n\n\n'
    for vdw in vdwList:
        prmString += vdw
    prmString += '\n\n\n'
    for bond in bondList:
        prmString += bond
    prmString += '\n\n\n'
    for angle in angleList:
        prmString += angle
    prmString += '\n\n\n'
    for ub in ubList:
        prmString += ub
    prmString += '\n\n\n'
    for imptor in imptorsList:
        prmString += imptor
    prmString += '\n\n\n'
    for torsion in torsionList:
        prmString += torsion
    prmString += '\n\n\n'

    with open(f'{nameroot}-qchem.prm', 'w+') as f:
        f.write(prmString)


for file in sys.argv[1:]:
    if file[-3:] == 'xyz':
        xyzfile = file
    if file[-3:] == 'key':
        keyfile = file

nameroot = xyzfile.split('.')[0]


ff2adj(xyzfile, keyfile, nameroot)