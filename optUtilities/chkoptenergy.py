#!python3
import matplotlib.pyplot as plt
import sys
import os

infilelist = []
for i in sys.argv[1:]:
    infilelist += [os.path.abspath(i)]

fig = plt.figure(figsize=(12,5))
ax = fig.add_subplot(111)
ax.set_xlabel("OPT Iteration")
ax.set_ylabel("Energy ($E_h$)")
fig.gca().ticklabel_format(axis='both', style='plain', useOffset=False)

labelname = []
for infile in infilelist:
    with open(infile, "r") as file:
        inputfile = file.read()
    x = []
    if "Psi4" in inputfile:
        print("Psi4")
        prog = 'psi4'
        searchterm = "Total Energy = "
        
    elif "This is part of the Gaussian(R)" in inputfile:
        print("Gaussian")
        prog = 'gaussian'
        searchterm = "SCF Done:  E("

    elif "* O   R   C   A *" in inputfile:
        print("ORCA")
        prog = 'orca'
        searchterm = "FINAL SINGLE POINT ENERGY"

    elif " x T B" in inputfile:
        print('XTB')
        prog = 'xtb'
        searchterm = 'total energy  :'
    
    inputfile = inputfile.split("\n")

    yrawlist = []
    y = []
    for i in inputfile:
        if searchterm in i:
            yrawlist += [i]
    
    if prog in ['psi4', 'gaussian', 'orca']:
        for i in yrawlist:
            for j in i.split():
                try:
                    y += [float(j)]
                except:
                    pass

    if prog in ['xtb']:
        for i in yrawlist:
            y += [float(i.split()[4])]

    for i in range(len(y)):
        y[i] = float(y[i])

    for i in range(len(y)):
        x.append(i)

    ax.plot(x, y, '.-')
    labelname += [str(str(infile.split("/")[-1].split(".")[0]))]


ax.legend(labelname)
plt.show()