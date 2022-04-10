import mdtraj as md
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import csv
import sys

nprocs = int(sys.argv[1])
path="/home/asnow/p2015120004/asnow/honours/MD-runs"
dcd="prod-dump.dcd"
psf="topol.psf"
rdfpic="mdtraj_rdf.png"
rdffile="mdtraj_rdf.csv"

ils = {"ct": ["N1", "=~ \'N[5-7]\'"], "co": ["N1", "S5"], "cm": ["N1", "S5"]}
basegeoms = ["na1r-s", "na1r-r", "na1p-s", "na1p-r", "na1t-1-r", "na1t-1-s", "na1t-2-r", "na1t-2-s", "na1t-3-r", "na1t-3-s"]
fields = ["0", "1"]

to_run = []
for il in ils.keys():
    for basegeom in basegeoms:
        for field in fields:
            to_run += ["{}-{}-{}".format(field,il,basegeom)]




def genRDF(jobname):
    try:
        traj = md.load("{}/{}/{}".format(path,jobname,dcd), top="{}/{}/{}".format(path,jobname,psf))
        pairs = traj.top.select_pairs("name {}".format(ils[il][0]), "name {}".format(ils[il][1]))
        bins, rdf = md.geometry.rdf.compute_rdf(traj, pairs, r_range=(0.0,2.0))
        bins *= 10  # nm to angstroms
        plt.plot(bins, rdf)
        plt.savefig("{}/{}/{}".format(path,jobname,rdfpic), dpi=300)
        rows = []
        for i in range(len(bins)):
            rows += [[bins[i], rdf[i]]]

        with open("{}/{}/{}".format(path,jobname,rdffile), "w") as f:
            g = csv.writer(f)
            for i in rows:
                g.writerow(i)
    except:
        print("failed for: {}".format(jobname))
        pass

Parallel(n_jobs=nprocs)(delayed(genRDF)(i) for i in to_run)