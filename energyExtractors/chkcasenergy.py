#!python3
from tkinter.messagebox import YES
import matplotlib.pyplot as plt
import sys
import os

infilelist = []
for i in sys.argv[1:]:
    infilelist += [os.path.abspath(i)]


labelname = []
fig = plt.figure(figsize=(12,5))

while True:
    ax = fig.add_subplot(111)
    ax.set_xlabel("CAS Iteration")
    ax.set_ylabel("Energy ($E_h$)")
    ax.ticklabel_format(useOffset=False)
    ax2 = ax.twinx()
    ax2.set_ylabel("ΔEnergy ($E_h$)")
    ax2.set_yscale('log')
    ax2.set_ylim(1e-10, 0)
    
    for infile in infilelist:
        with open(infile, "r") as file:
            inputfile = file.read()

        # ORCA specific settings
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
                    x = list(range(len(ye)))
            except:
                pass
        ax.plot(x, ye, '.-', label=str(str(infile.split("/")[-1].split(".")[0])))
        ax2.plot(x[1:], yde[1:], '.:', label=str(str(infile.split("/")[-1].split(".")[0])))
    ax.legend()
    plt.pause(20)
    plt.clf()