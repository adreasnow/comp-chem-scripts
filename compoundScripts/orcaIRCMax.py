import subprocess
import os

# This scripts performs an IRCmax calculatiuon using ORCA.
orcaroot = os.getenv('ORCA_ROOT') # directory from which to call orca, make sure that you've activated an orca module
memory = 16 # in GB, this will be multiplies by 1024 for openmpi
procs = 8


ircmax_range = 8 # the amount of steps either side of the TS to calculate at a higher level of theory
irc_string = "! irc m062x def2-TZVP CPCM" # the command with which to calculate the base IRC
ircmax_string = "! sp mp2 def2-QZVPP CPCM" # the command to refine the IRC gemetry

# geometry, charge and multiplicity specification
charge = -1
multiplicity = 1

geomblock = """
H     -0.423633   -0.005086    0.573558
O      0.271024   -0.484489    0.090909
C     -0.507040    0.172188   -1.860803
H     -1.295585   -0.550155   -1.706069
Br    -1.360589    0.861929   -3.949823
H     -0.587779    1.158005   -1.424359
H      0.440826   -0.151581   -2.267721
"""

# any extra blocks that you want to pass to ORCA
# these will be the same for the IRC and IRCmax jobs
extra_block = """
%cpcm
  smd true
  smdsolvent "Water"
end
"""

# defines the function to call orca
def runorca(job):
    mpiargs = "--mca btl_openib_warn_no_device_params_found 0 --mca pml ob1 --mca btl ^openib"

    proc = subprocess.run(f"{orcaroot}/orca {job}.inp {mpiargs} > {job}.out", executable='/bin/bash', shell=True)

# defines the functiuon to import the IRC xyz file
# this was stolen from another script of mine, so probably has some redundtant features...
def readXYZ(file):
    with open(file, "r") as f:
        lines = f.readlines()
    tmpgeom = []
    geom = []
    for i in lines:
        try:
            atoms = int(i)
            geom += [tmpgeom]
            tmpgeom = []
            tmpgeom += [atoms]
            skip = 0
        except:
            if i == "":
                pass
            if skip != 0:    
                # geom

                linelist = i.split()
                try:
                    tmpgeom += ["  {}    {}    {}    {}".format(linelist[0], linelist[1], linelist[2], linelist[3])]
                except:
                    pass
                skip += 1
            else:
                tmpgeom += [i.split("\n")[0]]
                skip += 1 
    geom += [tmpgeom]
    return(geom)

# sets up the scratch directory for job processing
cwd = os.getcwd()
os.mkdir(f"{cwd}/scratch")
os.chdir(f"{cwd}/scratch")

# writes the IRC job file
with open("irc.inp", "w") as f:
    f.write(f"{irc_string}\n\n")
    f.write(f"%maxcore {int((memory/procs)*1024)}\n\n")
    f.write(f"%pal\n\tnprocs {procs}\nend\n")
    f.write(f"{extra_block}\n")
    f.write(f"* xyz {charge} {multiplicity}{geomblock}*\n\n")

# runs the irc job
runorca("irc")

# reads in the irc output
irc_energy = {}
with open("irc.out", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        # finds the TS from the IRC run
        if "<= TS" in line:
            tsnum = int(line.split()[0])
            ts_linenum = i
    # pulls the IRC energy out from the IRC run
    counter = tsnum-ircmax_range
    for i in range(ts_linenum-ircmax_range, ts_linenum+ircmax_range+1):
        irc_energy[counter] = [float(lines[i].split()[1])]
        counter += 1

# Converts the enrgies to kj/mol from E_h and sets them relative to the TS
for i in irc_energy:
    irc_energy[i] += [irc_energy[i][0]-irc_energy[tsnum][0]]
    irc_energy[i] += [irc_energy[i][1]*2625.5]

# reads in the geometry from the IRC job for the IRCmax jobs
xyz = readXYZ("irc_IRC_Full_trj.xyz")
ircmax_energy = {}


for i in range(tsnum-ircmax_range, tsnum+ircmax_range+1):
    # writes the IRCmax jobs
    with open(f"ircmax_{i}.inp", "w") as f:
        ircmax_geom = '\n'.join(xyz[i][2:])
        f.write(f"{ircmax_string}\n\n")
        f.write(f"%maxcore {int((memory/procs)*1024)}\n\n")
        f.write(f"%pal\n\tnprocs {procs}\nend\n")
        f.write(f"{extra_block}\n")
        f.write(f"* xyz {charge} {multiplicity}\n{ircmax_geom}\n*\n\n")

    # runs the IRCmax jobs
    runorca(f"ircmax_{i}")

    # extracts the single point energy for the IRCmax jobs
    with open(f"ircmax_{i}.out", "r") as f:
        lines = f.readlines()
        for j, line in enumerate(lines):
            if "FINAL SINGLE POINT ENERGY" in line:
                ircmax_energy[i] = [float(line.split()[4])]

# identifies the new TS from the IRCmax jobs
max_e = -9999999999999999.0
max_e_num = 0
for i in ircmax_energy:
    if ircmax_energy[i][0] > max_e:
        max_e = ircmax_energy[i][0]
        max_e_num = i

# converts the enrgies to kj/mol from E_h and sets them relative to the TS
for i in ircmax_energy:
    ircmax_energy[i] += [ircmax_energy[i][0]-ircmax_energy[max_e_num][0]]
    ircmax_energy[i] += [ircmax_energy[i][1]*2625.5]

# writes out the results to the a convenient output file
with open(f"00-ircmax_results.out", "w") as f:
    f.write("IRC energy\n")
    f.write("\tStep #\tE_total\tE_hartree\tE_kjmol\n")
    for i in irc_energy:
        f.write("\t{}\t{}\t{}\t{}\n".format(i, irc_energy[i][0], irc_energy[i][1], irc_energy[i][2]))

    f.write("Final IRCmax energy\n")
    f.write("\tStep #\tE_total\tE_hartree\tE_kjmol\n")
    for i in ircmax_energy:
        f.write("\t{}\t{}\t{}\t{}\n".format(i, ircmax_energy[i][0], ircmax_energy[i][1], ircmax_energy[i][2]))
