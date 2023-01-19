#!python3
from tkinter.messagebox import YES
import matplotlib.pyplot as plt
import sys
import os

infilelist = []
for i in sys.argv[1:]:
    infilelist += [os.path.abspath(i)]

fig, ax = plt.subplots(figsize=(12,5))
ax.set_xlabel("CAS Iteration")
ax.set_ylabel("Energy ($E_h$)")
fig.gca().ticklabel_format(axis='both', style='plain', useOffset=False)

labelname = []
for infile in infilelist:
    with open(infile, "r") as file:
        inputfile = file.read()

    if "Psi4" in inputfile:
        print("Psi4 is not yet implemented")
        exit()
        
    elif "This is part of the Gaussian(R)" in inputfile:
        print("Gaussian is not yet implemented")
        exit()

    elif "* O   R   C   A *" in inputfile:
        print("ORCA")
        searchterm = "E(CAS)="
        energyPos = 1
        dePos = 4
    
    inputfile = inputfile.split("\n")

    ye = []
    yde = []
    x = []
    for i in inputfile:
        try:
            if searchterm in i:
                ye += [float(i.split()[energyPos])]
                yde += [abs(float(i.split()[dePos]))]
        except:
            pass

    x = list(range(len(ye)))
    ax.plot(x, ye, '.-', label=str(str(infile.split("/")[-1].split(".")[0])))
    ax2 = ax.twinx()
    ax2.set_yscale('log')
    ax2.set_ylim(1e-10, 0)
    ax2.plot(x[1:], yde[1:], '.:', label=str(str(infile.split("/")[-1].split(".")[0])))
    ax2.set_ylabel("ΔEnergy ($E_h$)")
    


ax.legend()
plt.show()