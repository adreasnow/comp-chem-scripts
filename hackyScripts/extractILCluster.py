import MDAnalysis as mda
from MDAnalysis import transformations
import sys

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
    
def runextract(ionpairs, dcdfile):
    def order_ions(ionpairs, u):
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
    
    filepath =  "/".join(dcdfile.split("/")[:-1])
    pdbname = dcdfile.split("/")[-1].split(".")[0]
    if filepath == "":
        filepath ="."
    psffile     = filepath + f"/topol.psf"

    u = mda.Universe(psffile, dcdfile, in_memory=True)

    core             = u.select_atoms("resname na1* and not type DP_")
    notcore          = u.select_atoms("not group core and not type DP_", core=core)

    workflow = [transformations.unwrap(core),
                transformations.center_in_box(core, center='mass'),
                transformations.wrap(notcore)]

    u.trajectory.add_transformations(*workflow)

    
    

    cations, anions = order_ions(ionpairs, u)
    counter = 1
    resids = ""
    filelist = []
    
    for j in range(1, ionpairs+1):
        if resids == "":
            resids = resids + " resid {} or resid {}".format(cations[j-1], anions[j-1])
        else:
            resids = resids + " or resid {} or resid {}".format(cations[j-1], anions[j-1])

        with mda.Writer(f"{pdbname}-il-{j}.xyz") as f:
            filelist += [f"{pdbname}-il-{j}.xyz"]
            aroundcore = u.select_atoms("not type DP_ and ({})".format(resids))
            f.write(aroundcore)

        with mda.Writer(f"{pdbname}-core.xyz") as g:
            filelist += [f"{pdbname}-core.xyz"]
            g.write(core)
        counter += 1
        
    
        
    for xyzfile in filelist:
        geoms = readXYZ(xyzfile)
        count = 0

        with open(xyzfile, "w") as f:
            for i in geoms:
                for j in i:
                    f.write(str(j) + "\n")

ionpairs = 5
dcdfile = sys.argv[1]
runextract(ionpairs, dcdfile)