#! python3
import matplotlib.pyplot as plt
import numpy as np
import sys

for infile in sys.argv[1:]:
    filename = infile.split("/")[-1].split(".")[0]


    # read in the iterp file
    f = open(infile, "r")

    # split the file by linebreaks
    blocks = f.read().split("\n\n")
    f.close()

    # get rid of the leading newline
    blocks[0] = str(blocks[0][1:])

    # pick out only the iteration data
    iterations = []
    for i in range(len(blocks)):
        if (i % 2) == 0:
            iterations += [blocks[i]]

            
    # make array of iterations, each entry consiting of an array of x and y coordinates
    cleaned_iterations = []
    for i in range(len(iterations)):
        current_iteration = iterations[i].split("\n")[2:]
        x = []
        y = []
        for j in range(len(current_iteration)):
            values = current_iteration[j].split()
            x += [float(values[0])]
            y += [float(values[2]) * 2625.5]
            
            # cleaned_current_iterations += [values]
        input_iterations = [x, y]
        cleaned_iterations += [input_iterations]


    fig, ax = plt.subplots(1, 1)
    ax.set_ylabel(r'Relative Energy ($kJ\cdot mol^{-1}$)')
    ax.set_xlabel(r"Reaction coordinate")
    ax.set_title(filename)
    for i in range(len(cleaned_iterations)):
        x = cleaned_iterations[i][0]
        y = cleaned_iterations[i][1]
        ax.plot(x, y, color='k', linewidth=0.5)
        ax.axhline(0, color="black", linewidth=0.5, linestyle='-')

    x = cleaned_iterations[-1][0]
    y = cleaned_iterations[-1][1]
    ax.plot(x, y, color='r', linewidth=1, marker=".")

    plt.show()
        
