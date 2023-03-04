#!python3
import subprocess
import os
import sys

def runbash(command):
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, text=True, executable='/bin/bash')
    output = proc.stdout.strip('\n')
    if output != "":
        return(output)
    
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


for filenum in range(1,len(sys.argv)):
    if sys.argv[filenum].endswith(".out"):
        inp = runbash("sed -n -e '/Geometry (in Angstrom)/,/--------/ p' " + str(sys.argv[filenum]))
        if inp != None:

            outfile = str(os.path.splitext(str(sys.argv[filenum]))[0]) + ".xyz"
            runbash("rm " + str(outfile))
            
            f = open(outfile, "a+")
            
            inplines = list(inp.splitlines())
            bufferlist = []
            count = 0
            totalcount = 1
            for i in range(len(inplines)):
                stripline = inplines[i].strip()
                splitline = stripline.split()
                if len(splitline) == 4 and hasNumbers(splitline[3]) == True:
                    bufferlist = bufferlist + [stripline]
                    count = count + 1
                else:
                    if count != 0:
                        f.write(str(count) + "\n")
                        f.write("Geometry structure " + str(totalcount) + "\n")
                        for j in range(len(bufferlist)):
                            f.write(str(bufferlist[j]) + "\n")
                        totalcount = totalcount + 1
                        count = 0
                        bufferlist = []
            f.close()
