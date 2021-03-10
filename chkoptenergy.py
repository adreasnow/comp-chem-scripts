#!python
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import subprocess
import re


def runbash(command):
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, executable='/bin/bash')
    output = proc.stdout.decode().strip('\n')
    if output != "":
        return(output)

infilelist = []
for i in sys.argv[1:]:
	infilelist += [runbash("readlink -f " + i)]



fig = plt.figure(figsize=(12,5))
ax = fig.add_subplot(111)
ax.set_xlabel("OPT Iteration")
ax.set_ylabel("Energy ($E_h$)")
fig.gca().ticklabel_format(axis='both', style='plain', useOffset=False)

labelname = []
for infile in infilelist:
	x = []

	if "Psi4" in str(runbash("cat '" + infile + "' | grep 'Psi4'")):
		print("Psi4")
		inp = str(subprocess.check_output("cat '" + infile + "' | grep 'Total Energy = ' | tr -s ' ' | cut -d' ' -f5", shell=True).decode())
		y = inp.split("\n")[:-1]
		
	elif "This is part of the Gaussian(R)" in str(runbash("cat '" + infile + "' | grep 'This is part of the Gaussian(R)'")):
		print("Gaussian")
		inp = str(subprocess.check_output("cat '" + infile + "' | grep 'SCF Done:  E(' | awk '{print $5}'", shell=True).decode())
		y = inp.split("\n")[:-1]

	elif "* O   R   C   A *" in str(runbash("cat '" + infile + "' | grep '* O   R   C   A *'")):
		print("ORCA")
		inp = str(subprocess.check_output("cat '" + infile + "' | grep 'FINAL SINGLE POINT ENERGY' | tr -s ' ' | cut -d' ' -f 5", shell=True).decode())
		y = inp.split("\n")[:-1]



	for i in range(len(y)):
		y[i] = float(y[i])

	for i in range(len(y)):
		x.append(i)

	ax.plot(x, y, '.-')
	labelname += [str(str(infile.split("/")[-1].split(".")[0]))]


ax.legend(labelname)
plt.show()