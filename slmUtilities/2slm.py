#! python3
import argparse
import os
import requests
import subprocess
from datetime import datetime
from time import sleep
from pathlib import Path
from dataclasses import dataclass
from aenum import AutoEnum

def read_args() -> argparse.ArgumentParser.parse_args:
    parser = argparse.ArgumentParser(
        description=(
            "Slurm script importer for MonARCH/M3"
        )
    )
    parser.add_argument(
        "-d",
        "--days",
        help="Days allowed for the job to run. If more granularity is needed, then use -H",
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-H",
        "--hours",
        help="Hours allowed for the job to run in the format HH - Superseeds -d",
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-s",
        "--short",
        default=False,
        help="Uses the shortest settings and queues. 24 hours for MonARCH (same as not setting any time flag). 30 minutes for Massive",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-m",
        "--memory",
        help="Memory allowed in GB (not Gb). Will be automatically populated if specified in the job file",
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-n",
        "--ntpn",
        help="Tasks per node. Defaults to the number of procs",
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-c",
        "--cpus",
        help="The amount of procs (CPUs) allowd for the job to run. Will be automatically populated if specified in the job file",
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-C",
        "--copy",
        help="List any files to copy, relative to the current dir",
        nargs=1,
        action='append',
        default=[],
        required=False,
    )
    parser.add_argument(
        "-p",
        "--partition",
        help="The partitons to be specified as comma separated values, comp,short will be automatically applied where needed",
        default=[''],
        nargs=1,
        required=False,
    )
    parser.add_argument(
        "-e",
        "--email",
        help="Sends an email to the user, as pulled form the system variable $EMAIL. Set this in your rc file",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-q",
        "--qos",
        help="QOS specification",
        nargs=1,
        default=[''],
        required=False,
    )
    parser.add_argument(
        "-o",
        "--normal",
        help="Use non-priority (nOrmal) qos",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-t",
        "--touch",
        help="this flag tells the ccript to 'touch' the log file. This forces the script to make sure that the logfile exists before the slurm job is run",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-S",
        "--submit",
        help="Submits job via SLURM",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Software version, choose from: For ORCA - 4 (ORCA 4.2.1) and 5 (ORCA 5.0.3) (default = 5), For Psi4 - 1.3 (Psi4 1.3.2), 1.4 (Psi4 1.4.1), , 1.4 (Psi4 1.5.0) (default = 1.5) Assumes Psi4 is installed with Miniconda in psi4-1.5",
        required=False,
        default=0.0,
    )
    parser.add_argument(
        "-D",
        "--dependency",
        help="SLURM dependency ('-d afterany:<JOBID>')",
        required=False,
        default=0,
        type=int,
    )
    parser.add_argument(
        "-P",
        "--projectdir",
        help="Works from project directory instead of scratch (ORCA and Psi4 only)",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-N",
        "--notify",
        help="""(notify) This is an advanced feature that allows you to creat a webhook input at ifttt.com
	    and will send a request with the values 
	      - value1:job name
	      - value2:status (submitted/running/finished)
	      - value3:tail of log file where value2=status
	    This requires two environment variables (exported from your .rc file)
	      - JOBID which is the name of the ifttt webhook
	      - JOBKEY which contains your API key""",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--local",
        help="Uses the local /mnt/scratch instead of the project's scratch",
        default=False,
        required=False,
        action="store_true"
    )
    parser.add_argument(
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()


def setupScratch(prop) -> None:
    prop.scratchStr += '# Setting up the scratch directory\n'
    prop.scratchStr += f'mkdir -p "{prop.scratchDir}"'
    prop.scratchStr += f'\ncp "{prop.fullFilePath}" "{prop.scratchDir}"'
    prop.scratchStr += f'\ncd "{prop.scratchDir}"\n'
    for file in prop.args.copy:
        prop.scratchStr += f'cp {os.path.abspath(file[0])} "{prop.scratchDir}"\n'
    prop.scratchStr += '\n\n'
    return

def copyScratch(prop) -> None:
    prop.scratchStr += '# copying files from the scratch directory\n'
    prop.scratchStr += f'mv "{prop.filePath}/{prop.fileName}" "{prop.filePath}/{prop.fileName}.bak.{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}"\n'
    prop.scratchStr += f'cp -r "{prop.scratchDir}" "{prop.filePath}/{prop.fileName}" && '
    prop.scratchStr += f'rm -rf "{prop.scratchDir}"\n'
    prop.scratchStr += f'mv "{prop.filePath}/{prop.fileName}.out" "{prop.filePath}/{prop.fileName}/"\n\n'
    return

def notifySubmit(prop) -> None:
    json = {'value1': prop.fileName, 'value2': 'submitted', 'value3': prop.cluster.hostName}
    r = requests.post(f'https://maker.ifttt.com/trigger/{os.environ["JOBID"]}/with/key/{os.environ["JOBKEY"]}', json=json, headers={"Content-Type": "application/json"})
    r = requests.post(f'https://api.adreasnow.com/id/{prop.fileName}/submitted/{prop.cluster.hostName}/')
    return

def notifyCall(state:str, prop) -> None:
    prop.scratchStr += f'# notifying of {state} job\n'
    prop.scratchStr += 'curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
    prop.scratchStr += f'curl -s -X POST https://api.adreasnow.com/id/{prop.fileName}/{state}/{prop.cluster.hostName}/\n'
    return

def runGaussian(prop) -> None:
    prop.scratchStr += f'# Running Gaussian job\n'
    prop.scratchStr += f'module load gaussian/g16a03'
    if prop.notify:
        state = 'failed'
        prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
    else:
        prop.scratchStr += '\n\n'
    prop.scratchStr += f'cat "{prop.fullFilePath}" | G16 > "{prop.filePath}/{prop.fileName}.out" 2>&1\n\n'

def runMopac(prop) -> None:
    prop.scratchStr += f'# Running MOPAC job\n'
    prop.scratchStr += f'source /monfs00/projects/p2015120004/apps/mopac/activate_mopac.sh\n\n'
    setupScratch(prop)
    if prop.args.touch == True:
        prop.scratchStr += f'touch "{prop.scratchDir}/{prop.fileName}.out"\n'
        prop.scratchStr += f'ln -s "{prop.scratchDir}/{prop.fileName}.out" "{prop.filePath}/{prop.fileName}.out"\n'
    prop.scratchStr += f'/usr/bin/time -v mopac "{prop.fileName}"'
    if prop.notify:
        state = 'failed'
        prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
    else:
        prop.scratchStr += '\n\n'
    if prop.args.touch == True: prop.scratchStr += f'rm "{prop.filePath}/{prop.fileName}.out"\n'
    copyScratch(prop)
    return


def runOrca(prop) -> None:
    if float(prop.args.version) in [4.0, 5.0]:
        orcaVersion = int(prop.args.version)
        print(f'Using ORCA {orcaVersion}')
    else:
        if float(prop.args.version) == 0.0:
            orcaVersion = 5
            print(f'Using ORCA {orcaVersion}')
        else:
            print(f'ORCA verison {prop.args.version} not recognised')
            orcaVersion = 5
            print(f'Using ORCA {orcaVersion}')


    prop.scratchStr += f'# Running ORCA job\n'
    if orcaVersion == 5: prop.scratchStr += f'source {prop.cluster.project}/apps/orca_5.0.4/activate_orca.sh\n\n'
    if orcaVersion == 4: prop.scratchStr += 'module unload orca/4.2.1\nmodule load orca/4.2.1-216\n\n'

    if prop.args.projectdir == True:
        prop.scratchStr += f'mkdir -p "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'cp "{prop.filePath}/{prop.fileName}.inp" "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'cd "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'/usr/bin/time -v $ORCA_ROOT/orca "{prop.fileName}.inp" "--mca pml ob1 --mca btl ^openib" > "{prop.filePath}/{prop.fileName}.out" 2>&1'
        if prop.notify:
            state = 'failed'
            prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
        else:
            prop.scratchStr += '\n\n'
        if prop.notify: notifyCall('finished', prop)
    else:
        setupScratch(prop)
        prop.scratchStr += f'/usr/bin/time -v $ORCA_ROOT/orca "{prop.fileName}.inp" "--mca pml ob1 --mca btl ^openib" > "{prop.filePath}/{prop.fileName}.out" 2>&1'
        if prop.notify:
            state = 'failed'
            prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
        else:
            prop.scratchStr += '\n\n'
        if prop.notify: notifyCall('finished', prop)
        copyScratch(prop)
    return

def runPsi4(prop) -> None:
    prop.scratchStr += f'# Running Psi4 job\n'
    if float(prop.args.version) in [1.3, 1.4, 1.5, 1.6]:
        psi4Version = float(prop.args.version)
        print(f'Using Psi4 {psi4Version}')
    else:
        if float(prop.args.version) == 0.0:
            psi4Version = 1.6
            print(f'Using Psi4 {psi4Version}')
        else:
            print(f'Psi4 verison {prop.args.version} not recognised')
            psi4Version = 1.6
            print(f'Using Psi4 {psi4Version}')
    
    if psi4Version == 1.3: prop.scratchStr += 'module load psi4/v1.3.2\n\n'
    if psi4Version in [1.4, 1.5, 1.6]: prop.scratchStr += f'source {prop.cluster.project}/apps/psi4-{psi4Version}/activate_psi4_job.sh\n\n'

    prop.scratchStr += f'export PSIPATH=$PSIPATH:{prop.cluster.homePath}/basis\n'
    if prop.args.projectdir == True:
        prop.scratchStr += f'export PSI_SCRATCH="{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'mkdir -p "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'cp "{prop.filePath}/{prop.fileName}.inp" "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'cd "{prop.filePath}/{prop.fileName}"\n'
        prop.scratchStr += f'/usr/bin/time -v psi4 -i "{prop.fileName}.in" -o "{prop.fileName}.out" 2>&1'
        if prop.notify:
            state = 'failed'
            prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
        else:
            prop.scratchStr += '\n\n'
    else:
        prop.scratchStr += f'export PSI_SCRATCH="{prop.scratchDir}"\n\n'
        setupScratch(prop)
        prop.scratchStr += f'/usr/bin/time -v psi4 -i "{prop.fileName}.in" -o "{prop.filePath}/{prop.fileName}.out" 2>&1'
        if prop.notify:
            state = 'failed'
            prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
        else:
            prop.scratchStr += '\n\n'
        copyScratch(prop)

    return

def runQChem(prop) -> None:
    prop.scratchStr += '\n# Set up environment\n' 
    prop.scratchStr += 'module load qchem/6.0.2\n\n'
    prop.scratchStr += f'export QCSCRATCH=/mnt/lustre/scratch/{prop.cluster.user}/qchem\n'
    prop.scratchStr += '# Setting up the scratch directory\n' 
    prop.scratchStr += f'mkdir -p "{prop.filePath}/{prop.fileName}"\n'
    prop.scratchStr += f'cp "{prop.fullFilePath}" "{prop.filePath}/{prop.fileName}"\n'
    prop.scratchStr += f'cd "{prop.filePath}/{prop.fileName}"\n\n'
    prop.scratchStr += '# Run Q-Chem\n' 
    prop.scratchStr += f'/usr/bin/time -v qchem -slurm -nt {prop.procs} "{prop.fileName}.inp" "{prop.filePath}/{prop.fileName}.out"'
    if prop.notify:
        state = 'failed'
        prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
    else:
        prop.scratchStr += '\n\n'
    prop.scratchStr += '# Copy log file over\n' 
    prop.scratchStr += f'mv "{prop.filePath}/{prop.fileName}.out" "{prop.filePath}/{prop.fileName}"\n\n'
    return

def runNWChem(prop) -> None:
    global fullFilePath
    global scratchStr
    global fileName
    global scratchDir
    prop.scratchStr += '\n# Set up environment\n' 
    prop.scratchStr += f'source {prop.cluster.project}/apps/nwchem/activate_nwchem_7.2.0.sh\n'
    setupScratch(prop)
    prop.scratchStr += '# Run NWChem\n' 
    prop.scratchStr += f'cd {prop.scratchDir}\n' 
    prop.scratchStr += f'export OMP_NUM_THREADS {prop.procs}\n' 
    prop.scratchStr += f'export ARMCI_NETWORK=OPENIB\n'
    prop.scratchStr += f'export ARMCI_OPENIB_DEVICE mlx4_0\n' 
    prop.scratchStr += f'/usr/bin/time -v mpirun -n {prop.procs+1} --oversubscribe $BINDIR/nwchem "{prop.fileName}.nw" > "{prop.filePath}/{prop.fileName}.out"'
    if prop.notify:
        state = 'failed'
        prop.scratchStr += '|| curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "\'`echo $SLURM_JOB_NAME | cut -d\'.\' -f 1`\'" , "value2": "' + state + '", "value3": "' + prop.cluster.hostName + '"}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'
    else:
        prop.scratchStr += '\n\n'
    copyScratch(prop)
    return

@dataclass
class Cluster():
    def __init__(self) -> None:
        self.hostname = os.uname().nodename
        print(f'Hostname: {self.hostname}')
        if self.hostname.startswith('monarch'):
            self.host = self._cluster.MONARCH
        elif self.hostname.startswith('gadi-'):
            self.host = self._cluster.GADI
            print('Gadi not implemented!\nExiting...')
            exit()
        elif self.hostname.startswith('m3'):
            self.host = self._cluster.M3

        if self.host == self._cluster.GADI:
            self.hostName = 'Gadi'
            self.user = os.getlogin()
            self.account = 'k96'
            self.scratch = f'/home/{self.user}/{self.account}_scratch/{self.user}'
            self.project = f'/g/data/{self.account}'
            self.homePath = f'{self.project}/{self.user}'
        elif self.host == self._cluster.MONARCH:
            self.hostName = 'MonARCH'
            self.user = os.getlogin()
            self.scratch = f'/home/{self.user}/scratch'
            self.account = 'p2015120004'
            self.project = f'/mnt/lustre/projects/{self.account}'
            self.homePath = f'{self.project}/{self.user}'
        elif self.host == self._cluster.M3:
            self.host = 'm3'
            self.hostName = 'M3'
            self.user = os.getlogin()
            self.account = 'sn29'
            self.scratch = f'/scratch/{self.account}/{self.user}'
            self.project = f'/projects/{self.account}'
            self.homePath = f'{self.project}/{self.user}'
        else:
            print('Cluster not recognised.\nExiting...')
            exit()
        return

    class _cluster(AutoEnum):
        GADI = 'Gadi'
        MONARCH = 'MonARCH'
        M3 = 'M3' 

class Program(AutoEnum):
        ORCA = "ORCA"
        QCHEM = 'Q-Chem'
        MOPAC = 'Mopac'
        NWCHEM = 'NWChem'
        GAUSSIAN = 'Gaussian'
        PSI4 = 'Psi4'

@dataclass
class Properties():
    args: dict
    cluster: Cluster
    copy: bool = None
    notify: bool = None
    short: bool = None
    touch: bool = None
    scratchStr: str = ''
    fullFilePath: str = ''
    program: Program = None
    filePath: str = ''
    fileName: str = ''
    scratchDir: str = ''
    procs: int = None
    mem: int = None
    tpn: int = None
    timestring: str = ''
    part: str = ''
    qos: str = ''

    def __post_init__(self):
        for arg in self.args.files:
            if arg.startswith('-'):
                print(f'{arg} is not a recognised flag.\nExiting..')
                exit() 
        self.copy = self.args.copy, 
        self.notify = self.args.notify
        self.short = self.args.short
        self.touch = self.args.touch
        if self.args.local == True:
            self.cluster.scratch = '/mnt/scratch'

    def setupTime(self) -> None:
        if self.short:
            if self.cluster.host == Cluster._cluster.MONARCH:
                self.timestring = '24:00:00'
            elif self.cluster.host == Cluster._cluster.M3:
                self.timestring == '00:30:00'
                self.qos = f'shortq,{self.args.qos[0]}' if len(self.args.qos[0]) > 0 else 'shortq'
                self.part = f'shortq,{self.args.partition[0]}' if len(self.args.partition[0]) > 0 else 'shortq'
        elif self.args.days[0] > 0:
            self.timestring = f'{self.args.days[0]*24}:00:00'
        elif self.args.hours[0] > 0:
            self.timestring = f'{self.args.hours[0]:02}:00:00'
        else:
            self.timestring = f'24:00:00'

        if self.cluster.host == Cluster._cluster.MONARCH:
            self.part = f'comp,{self.args.partition[0]}' if len(self.args.partition[0]) > 0 else 'comp'
            self.part = f'{self.part},short' if int(self.timestring.split(':')[0]) <= 24 else self.part
            self.qos = 'partner' if self.args.normal == False else self.args.qos[0] if len(self.args.qos[0]) > 0 else ''
        return

    def extractParams(self) -> None:
        with open(self.fullFilePath, 'r') as f:
            lines = f.readlines()
        self.mem = 0
        self.procs = 0
        
        for line in lines:
            if self.program == Program.GAUSSIAN:
                if 'nprocs' in line.lower():
                    self.procs = int(line.split('=')[1])
                if 'mem' in line.lower():
                    self.mem = int(''.join([s for s in list(line.split('=')[1]) if s.isdigit()]))
            if self.program == Program.ORCA:
                if 'nprocs' in line.lower():
                    self.procs = int(line.split()[1])
                if 'maxcore' in line.lower():
                    self.mem = int(line.split()[1])*1.05
                    print('ORCA is best with a small memory headroom, allocating an extra 5%')
            if self.program == Program.PSI4:
                if 'set_num_threads' in line.lower():
                    self.procs = int(line.split('(')[1].split(')')[0])
                if 'memory' in line.lower():
                    self.mem = int(''.join([s for s in list(line.split()[1]) if s.isdigit()]))
            if self.program == Program.QCHEM:
                if 'mem_total' in line.lower():
                    self.mem = int(line.split()[1])*1.15
                    print('QChem need a small memory headroom, allocating an extra 15%')
            if self.program == Program.NWCHEM:
                if 'memory' in line.lower() and 'total' in line.lower():
                    self.mem = int(line.split()[2])
            if self.program == Program.MOPAC:
                if 'threads' in line.lower():
                    for i in line.split():
                        if 'threads' in i:
                            self.procs = int(i.split('=')[1])

        self.procs = self.args.cpus[0] if self.args.cpus != [0] else self.procs

        if self.program == Program.ORCA:
            self.mem = int(round((self.mem*self.procs)/1024, 0))
        if self.program == Program.NWCHEM:
            self.mem = int((self.mem*self.procs))
        if self.program == Program.QCHEM:
            self.mem = int(round(self.mem/1024, 0))

        if self.procs == 0:
            self.procs = 1 if self.program not in [Program.QCHEM, Program.NWCHEM] else 16
            print(f'Number of cores not identified, using {self.procs} default')
            
        self.mem = self.args.memory[0] if self.args.memory[0] != 0 else self.mem
        if self.mem == 0:
            print('Memory not identified, using 32GB default')
            self.mem = 32
        self.tpn = self.args.ntpn[0] if self.args.ntpn[0] != 0 else self.procs
        return

def main() -> None:
    fileEXTs = {'mop': Program.MOPAC,
                'inp': Program.ORCA,
                'gjf': Program.GAUSSIAN,
                'com': Program.GAUSSIAN,
                '.in': Program.PSI4,
                '.nw': Program.NWCHEM}

    prop = Properties(read_args(), Cluster())


    for infile in prop.args.files:
        prop.scratchStr = '#!/bin/bash\n'
        try:
            if os.path.isfile(infile) == False:
                raise Exception()
        except:
            print(f'input file "{infile}" not found.\nNot processing.')
            continue
        prop.fullFilePath = os.path.abspath(infile)
        try:
            prop.program = fileEXTs[infile[-3:]]
        except:
            print('File type not recognised.\nNot processing.')
            continue

        #if .inp, then check if qchem
        if prop.program in [Program.ORCA, Program.PSI4]:
            with open(prop.fullFilePath, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if '$rem' in line:
                    prop.program = Program.QCHEM

        prop.filePath = '/'.join(prop.fullFilePath.split('/')[0:-1])
        prop.fileName = infile.split('/')[-1].split('.')[0]
    
        prop.scratchDir = f'{prop.cluster.scratch}/{prop.fileName}'
        prop.extractParams()
        prop.setupTime()

        prop.scratchStr += f'#SBATCH --time={prop.timestring}\n'
        prop.scratchStr += f'#SBATCH --ntasks={prop.procs}\n'
        prop.scratchStr += f'#SBATCH --cpus-per-task=1\n'
        prop.scratchStr += f'#SBATCH --ntasks-per-node={prop.tpn}\n'
        prop.scratchStr += f'#SBATCH --mem={prop.mem}GB\n'
        prop.scratchStr += f'#SBATCH --qos={prop.qos}\n' if len(prop.qos) > 0 else ''
        prop.scratchStr += f'#SBATCH --partition={prop.part}\n' if len(prop.part) > 0 else ''
        if prop.args.email: prop.scratchStr += f'#SBATCH --mail-type=ALL --mail-user={os.environ["EMAIL"]}\n'
        if prop.cluster.host == Cluster._cluster.M3 : prop.scratchStr += f'#SBATCH --account={prop.cluster.account}\n' 
        prop.scratchStr += f'\nexport PROJECT="{prop.cluster.account}"\n\n'
        

        if prop.notify: notifyCall('running', prop)

        if prop.program == Program.GAUSSIAN: runGaussian(prop)
        if prop.program == Program.MOPAC: runMopac(prop)
        if prop.program == Program.ORCA: runOrca(prop)
        if prop.program == Program.PSI4: runPsi4(prop)
        if prop.program == Program.QCHEM: runQChem(prop)
        if prop.program == Program.NWCHEM: runNWChem(prop)

        if prop.notify and prop.program != Program.ORCA: notifyCall('finished', prop)

        with open(f'{prop.filePath}/{prop.fileName}.slm', 'w') as slmFile:
            slmFile.write(prop.scratchStr)

        sleep(0.2)

        depcommand = f'-d afterok:{prop.args.dependency}' if prop.args.dependency > 0 else ''
        if prop.args.submit:
            command = f'cd "{prop.filePath}"; sbatch {depcommand} "{prop.filePath}/{prop.fileName}.slm"'
            attempts = 0
            while attempts < 3:
                try:
                    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, executable='/bin/bash')
                    out = proc.stdout.strip('\n')
                    err = proc.stderr.strip('\n')
                    if err != "": 
                        print(err)
                        raise Exception('err')
                    else:
                        print(out)
                        break
                except Exception('err'):
                    attempts += 1

            if prop.notify: notifySubmit(prop)

        if prop.args.touch and prop.program != Program.MOPAC: Path(f'{prop.filePath}/{prop.fileName}.out').touch()
    return

if __name__ == "__main__":
    main()