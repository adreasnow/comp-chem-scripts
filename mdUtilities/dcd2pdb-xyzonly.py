#!python3
import MDAnalysis as mda
from MDAnalysis import transformations
import sys

ionpairs = 10

def order_ions(ionpairs):
    cations = []
    anions = []
    for i in range(10, 150, 2):
        atoms = u.select_atoms("sphlayer {} {} group core and not type DP_".format(i/10, (i+2)/10), core=core)
        for j in list(atoms):
            fields = str(j).split()
            if fields[8] == "c4c1pyrr,":
                if fields[10] not in cations:
                    cations += [fields[10]]
            if fields[8] == "otf," or fields[8] == "tcm," or fields[8] == "mso4,":
                if fields[10] not in anions:
                    anions += [fields[10]]
    return(cations[0:ionpairs], anions[0:ionpairs])

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
                    tmpgeom += ["  {}    {}    {}    {}".format(linelist[0][0], linelist[1], linelist[2], linelist[3])]
                except:
                    pass
                skip += 1
            else:
                tmpgeom += [i.split("\n")[0]]
                skip += 1 
    geom += [tmpgeom]
    return(geom[1:])

for dcdfile in sys.argv[1:]:
    if dcdfile[-13:] == "prod-dump.dcd":
        filepath =  "/".join(dcdfile.split("/")[:-1])
        pdbname = dcdfile.split("/")[-1].split(".")[0]
        if filepath == "":
            filepath ="."
        psffile     = filepath + "/topol.psf"
        pdbfile     = filepath + "/{}.pdb".format(pdbname)
        pymolfile   = filepath + "/{}.pml".format(pdbname)
        corepdbfile = filepath + "/{}-core.pdb".format(pdbname)
        ilfile = filepath + "/{}-ils.xyz".format(pdbname)
        corefile = filepath + "/{}-core.xyz".format(pdbname)
        # aroundcorepdbfile = filepath + "/{}-aroundcore.pdb".format(pdbname)
        
        u = mda.Universe(psffile, dcdfile, in_memory=True)

        core             = u.select_atoms("resname na1* and not type DP_")
        notcore          = u.select_atoms("not group core and not type DP_", core=core)
    
        workflow = [transformations.unwrap(core),
                    transformations.center_in_box(core, center='mass'),
                    transformations.wrap(notcore)]

        u.trajectory.add_transformations(*workflow)


        with mda.Writer(ilfile, multiframe=True) as f:
            with mda.Writer(corefile, multiframe=True) as g:
                counter = 0
                for ts in u.trajectory:
                    if counter == 100:
                        cations, anions = order_ions(ionpairs)
                        resids = ""
                        for i in range(0, ionpairs):
                            if resids == "":
                                resids = resids + " resid {} or resid {}".format(cations[i], anions[i])
                            else:
                                resids = resids + " or resid {} or resid {}".format(cations[i], anions[i])

                        aroundcore = u.select_atoms("not type DP_ and ({})".format(resids))
                        print(len(list(core)) + len(list(aroundcore)))
                        f.write(aroundcore)
                        g.write(core)
                        counter = 1
                    counter += 1
            
        for xyzfile in [ilfile, corefile]:
            geoms = readXYZ(xyzfile)
            count = 0

            with open(xyzfile, "w") as f:
                for i in geoms:
                    for j in i:
                        f.write(str(j) + "\n")