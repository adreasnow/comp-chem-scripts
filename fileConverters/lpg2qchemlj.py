#! python3

import sys

def ff2adj(xyzfile, keyfile):

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

    for count, atom in enumerate(xyzList):
        print(f'{atom[0]} {atom[1]:15f} {atom[2]:15f} {atom[3]:15f} {-count-1:6d} {atom[5]:6d} {atom[6]:6d} {atom[7]:6d} {atom[8]:6d}')


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
                atomDict[splitLine[1]] += [float(splitLine[2]), float(splitLine[3])]
            elif splitLine[0] == 'charge':
                atomDict[splitLine[1]] += [float(splitLine[2])]
        except:
            pass

    print(f'\n\n$force_field_params\n   NumAtomTypes {len(atomDict)+30}')
    for count, atom in enumerate(atomDict):
        print(f'   AtomType {-count-1:7d} {atomDict[atom][3]:< 6.4f} {atomDict[atom][1]:< 6.4f} {atomDict[atom][2]:< 6.4f}')
    print('$end')


for file in sys.argv[1:]:
    if file[-3:] == 'xyz':
        xyzfile = file
    if file[-3:] == 'key':
        keyfile = file

ff2adj(xyzfile, keyfile)