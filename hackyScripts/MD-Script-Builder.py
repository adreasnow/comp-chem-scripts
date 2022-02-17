#!python3
import os
import subprocess
from joblib import Parallel, delayed
import requests
url = "https://maker.ifttt.com/trigger/job_id_done/with/key/eEvfCdvzr4jy_SX51JYjKhAILZjPa53n8MFcQd1FErB"

def runbash(commandlist):
    proc = subprocess.run(commandlist[0], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, executable='/bin/bash')
    output = proc.stdout.decode().strip('\n')
    print(output)
    proc = subprocess.run("/home/asnow/bin/sbatchall.sh {}".format(commandlist[1]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False, executable='/bin/bash')
    output = proc.stdout.decode().strip('\n')
    print(output)
    jobname = commandlist[1].split(".")[0]
    jobname = jobname.split("/")[-1]
    if proc.returncode == 0:
        myobj = {'value1': jobname, 'value2': 'submitted', 'value3': " "}
        requests.post(url, data=myobj)
    

parent = ""
ff = "/mnt/lustre/projects/p2015120004/asnow/ilmd-2ac/ff"
jobpath = "/mnt/lustre/projects/p2015120004/asnow/ilmd-2ac/MD-runs"
moleculecount = "500 500 1"
boxsize = "60"
ljscale = "{}/ljscale.ff".format(ff)
alpha = "{}/alpha.ff".format(ff)
npttime = 10
equiltime = 10
prodtime = 100
field = 1.0
acceleration = 0
# acceleration = 0.02

temp=343.15
il = [["{}/c4c1pyrr.zmat {}/tcm.xyz".format(ff, ff), "{}/il.ff".format(ff), "1-ct"],
      ["{}/c4c1pyrr.zmat {}/mso4.zmat".format(ff, ff), "{}/il.ff".format(ff), "1-cm"],
      ["{}/c4c1pyrr.zmat {}/otf.zmat".format(ff, ff), "{}/il.ff".format(ff), "1-co"],
      ["{}/c4c1pyrr.zmat {}/tcm.xyz".format(ff, ff), "{}/il.ff".format(ff), "0-ct"],
      ["{}/c4c1pyrr.zmat {}/mso4.zmat".format(ff, ff), "{}/il.ff".format(ff), "0-cm"],
      ["{}/c4c1pyrr.zmat {}/otf.zmat".format(ff, ff), "{}/il.ff".format(ff), "0-co"]]



na1 = [["{}/na1r-s.xyz".format(ff), "{}/na1r.ff {}/alpha-na1r.ff".format(ff, ff), "na1r-s"],
       ["{}/na1r-r.xyz".format(ff), "{}/na1r.ff {}/alpha-na1r.ff".format(ff, ff), "na1r-r"],
       ["{}/na1p-s.xyz".format(ff), "{}/na1p.ff {}/alpha-na1p.ff".format(ff, ff), "na1p-s"],
       ["{}/na1p-r.xyz".format(ff), "{}/na1p.ff {}/alpha-na1p.ff".format(ff, ff), "na1p-r"],
       ["{}/na1t-1-r.xyz".format(ff), "{}/na1t-1.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-1-r"],
       ["{}/na1t-1-s.xyz".format(ff), "{}/na1t-1.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-1-s"],
       ["{}/na1t-2-r.xyz".format(ff), "{}/na1t-2.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-2-r"],
       ["{}/na1t-2-s.xyz".format(ff), "{}/na1t-2.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-2-s"],
       ["{}/na1t-3-r.xyz".format(ff), "{}/na1t-3.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-3-r"],
       ["{}/na1t-3-s.xyz".format(ff), "{}/na1t-3.ff {}/alpha-na1t.ff".format(ff, ff), "na1t-3-s"]]

npttimeline = "{}_000_000".format(npttime)
equiltimeline = "{}_000_000".format(equiltime)
prodtimeline = "{}_000_000".format(prodtime)
prodcpttime = (npttime + equiltime)*1000000
nptcpttime = (npttime)*1000000
      
slm = ["""#!/bin/bash -l
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=16G
#SBATCH --gres=gpu:P100:1
#SBATCH --time=96:00:00
#SBATCH --partition=gpu
#SBATCH --qos=partner


############################################# ENV SETUP #############################################
module load openmm-velocity-verlet/.7.4
export PYTHONPATH=$PYTHONPATH:/mnt/lustre/projects/p2015120004/apps/openmm-opls:/mnt/lustre/projects/p2015120004/apps/openmm-opls/ms-tools


############################################# JOB SETUP #############################################
"""]
slm += ["jobname=\"{}\"\n"]
slm += ["jobpath=\"{}/$jobname\"\n"]
slm += ["""
run_bulk="/mnt/lustre/projects/p2015120004/asnow/ilmd-2ac/bin/run-bulk.py"
gro="./conf.gro"
psf="./topol.psf"
prm="./ff.prm"
cpt="./npt.cpt"
"""]
slm += ["npttime=\"{}\"\n".format(npttimeline)]
slm += ["equiltime=\"{}\"\n".format(equiltimeline)]
slm += ["prodtime=\"{}\"\n".format(prodtimeline)]
slm += ["equilcpttime=\"{}\"\n".format(prodcpttime)]
slm += ["nptcpttime=\"{}\"\n".format(nptcpttime)]
slm += ["temp={}\n".format(temp)]
slm += ["acceleration={}\n".format(acceleration)]
slm += ["field={}  # 0.05 V/nm = 0.005 V/Å = 0.005 au in LAMMPS".format(field)]
slm += ["""
cd $jobpath
############################################# NOTIFY #############################################
echo '{' 																		>> ./data.json
echo "  \\"value1\\":\\"$jobname\\","												>> ./data.json
echo '  "value2":"running",' 													>> ./data.json
echo '  "value3":" "'															>> ./data.json
echo '}' 																		>> ./data.json
curl -s -X POST -H "Content-Type: application/json" -d "@data.json" https://maker.ifttt.com/trigger/job_id_done/with/key/eEvfCdvzr4jy_SX51JYjKhAILZjPa53n8MFcQd1FErB > /dev/null
rm -rf ./data.json


############################################# JOB RUN #############################################
############### NPT # -n is in fs
time python3 $run_bulk --gro $gro --psf $psf --prm $prm -t $temp --thermostat nose-hoover --barostat iso -p 1 -n $npttime --min 10000 >& npt.log
cp cpt.cpt_$nptcpttime npt.cpt
mv dump.dcd npt-dump.dcd

############### NVT
time python3 $run_bulk --gro $gro --psf $psf --prm $prm -t $temp --thermostat nose-hoover --barostat no -n $equiltime --cpt $cpt --field $field --cos $acceleration >& equil.log
mv dump.dcd equil-dump.dcd
mv viscosity.txt equil-viscosity.txt
time python3 $run_bulk --gro $gro --psf $psf --prm $prm -t $temp --thermostat nose-hoover --barostat no -n $prodtime --cpt cpt.cpt_$equilcpttime --field $field --cos $acceleration >& prod.log
mv dump.dcd prod-dump.dcd

__conda_setup="$('/home/asnow/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/asnow/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/asnow/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/asnow/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup

python3 /home/asnow/bin/dcd2pdb.py *.dcd >& dcd2pdb.log

############################################# NOTIFY #############################################
echo '{' 																		>> ./data.json
echo "  \"value1\":\"$jobname\","												>> ./data.json
echo '  "value2":"finished",' 													>> ./data.json
echo '  "value3":" "'															>> ./data.json
echo '}' 																		>> ./data.json
curl -s -X POST -H "Content-Type: application/json" -d "@data.json" https://maker.ifttt.com/trigger/job_id_done/with/key/eEvfCdvzr4jy_SX51JYjKhAILZjPa53n8MFcQd1FErB > /dev/null
rm -rf ./data.json
"""]

try:        
    os.mkdir(jobpath)
except:
    pass
count = 1

createlist = []
for i in il:
    for j in na1:
        if count < 100:
            jobname = "{}-{}".format(i[2], j[2])
            if jobname in ["1-ct-na1t-1-r"]:
                if jobname[:2] == "1-":
                    field = 1.0
                if jobname[:2] == "0-":
                    field = 0.0
                slm[11] = "field={}  # 0.05 V/nm = 0.005 V/Å = 0.005 au in LAMMPS".format(field)
        
                try:
                    os.mkdir("{}/{}".format(jobpath, jobname))
                except:
                    pass
                with open("{}/{}/{}.slm".format(jobpath, jobname, jobname), "w") as g:
                    g.write(slm[0])
                    g.write(slm[1].format(jobname))
                    g.write(slm[2].format(jobpath))
                    for k in slm[3:]:
                        g.write(k)
                    createlist.append(["cd {}/{} ; python3 /home/asnow/bin/create_openmm.py -f {} {} -n {} -b {} -ff {} {} {} -s {} -d".format(
                            jobpath, jobname, i[0], j[0], moleculecount, boxsize, i[1], j[1], alpha, ljscale), "{}/{}/{}.slm".format(jobpath, jobname, jobname)])
            count += 1

# for i in createlist:
#     print(i[0].split(";")[0])
Parallel(n_jobs=3)(delayed(runbash)(i) for i in createlist)

