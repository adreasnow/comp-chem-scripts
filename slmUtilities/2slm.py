#! python3
import argparse
import os
import requests
import subprocess
from time import sleep
from pathlib import Path

def read_args():
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
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()


def setupScratch():
    global copy
    global scratchStr
    global scratchDir
    global fullFilePath
    global fileName
    scratchStr += '# Setting up the scratch directory\n'
    scratchStr += f'mkdir "{scratchDir}"'
    scratchStr += f'\ncp "{fullFilePath}" "{scratchDir}"'
    scratchStr += f'\ncd "{scratchDir}"\n'
    for file in copy:
        scratchStr += f'cp {os.path.abspath(file[0])} "{scratchDir}"\n'
    scratchStr += '\n\n'
    return

def copyScratch():
    global scratchStr
    global scratchDir
    global filePath
    global fileName
    scratchStr += '# copying files from the scratch directory\n'
    scratchStr += f'mkdir "{filePath}/{fileName}"\n'
    scratchStr += f'cp -r {scratchDir}/* "{filePath}/{fileName}/" && '
    scratchStr += f'rm -rf {scratchDir}\n'
    scratchStr += f'mv "{filePath}/{fileName}.out" "{filePath}/{fileName}/"\n\n'
    return

def notifySubmit():
    global fileName
    json = {'value1': fileName, 'value2': 'submitted', 'value3': ''}
    r = requests.post(f'https://maker.ifttt.com/trigger/{os.environ["JOBID"]}/with/key/{os.environ["JOBKEY"]}', json=json, headers={"Content-Type": "application/json"})
    return

def notifyCall(state, log=''):
    global scratchStr
    global fileName
    scratchStr += f'# notifying of {state} job\n'
    scratchStr += 'curl -s -X POST -H "Content-Type: application/json" -d \'{"value1": "' + fileName + '" , "value2": "' + state + '", "value3": ""}\' https://maker.ifttt.com/trigger/$JOBID/with/key/$JOBKEY > /dev/null\n'

    return

def runGaussian():
    global fileName
    global fullFilePath
    global filePath
    global scratchStr
    scratchStr += f'# Running Gaussian job\n'
    scratchStr += f'module load gaussian/g16a03\n\n'
    scratchStr += f'cat "{fullFilePath}" | G16 > "{filePath}/{fileName}.out" 2>&1\n\n'

def runMopac(args):
    global fullFilePath
    global scratchStr
    global scratchDir
    global fileName
    scratchStr += f'# Running MOPAC job\n'
    scratchStr += f'source /monfs00/projects/p2015120004/apps/mopac/activate_mopac.sh\n\n'
    setupScratch()
    if args.touch == True:
        scratchStr += f'touch "{scratchDir}/{fileName}.out"\n'
        scratchStr += f'ln -s "{scratchDir}/{fileName}.out" "{filePath}/{fileName}.out"\n'
    scratchStr += f'/usr/bin/time -v mopac "{fileName}" \n\n'
    if args.touch == True: scratchStr += f'rm "{filePath}/{fileName}.out"\n'
    copyScratch()


def runOrca(args):
    global scratchStr
    global project
    global filePath
    global fileName

    if float(args.version) in [4.0, 5.0]:
        orcaVersion = int(args.version)
        print(f'Using ORCA {orcaVersion}')
    else:
        if float(args.version) == 0.0:
            orcaVersion = 5
            print(f'Using ORCA {orcaVersion}')
        else:
            print(f'ORCA verison {args.version} not recognised')
            orcaVersion = 5
            print(f'Using ORCA {orcaVersion}')


    scratchStr += f'# Running ORCA job\n'
    if orcaVersion == 5: scratchStr += f'source {project}/apps/orca_5.0.3/activate_orca.sh\n\n'
    if orcaVersion == 4: scratchStr += 'module unload orca/4.2.1\nmodule load orca/4.2.1-216\n\n'

    mpiargs="--mca btl_openib_warn_no_device_params_found 0 --mca pml ob1 --mca btl ^openib"
    if args.projectdir == True:
        scratchStr += f'mkdir "{filePath}/{fileName}"\n'
        scratchStr += f'cp "{filePath}/{fileName}.inp" "{filePath}/{fileName}"\n'
        scratchStr += f'cd "{filePath}/{fileName}"\n'
        scratchStr += f'/usr/bin/time -v $ORCA_ROOT/orca "{fileName}.inp" "{mpiargs}" > "{filePath}/{fileName}.out" 2>&1\n\n'
    else:
        setupScratch()
        scratchStr += f'/usr/bin/time -v $ORCA_ROOT/orca "{fileName}.inp" "{mpiargs}" > "{filePath}/{fileName}.out" 2>&1\n\n'
        copyScratch()
    return

def runPsi4(args):
    global scratchStr
    global project
    global filePath
    global fileName
    global homePath
    global scratchDir
    scratchStr += f'# Running Psi4 job\n'
    if float(args.version) in [1.3, 1.4, 1.5]:
        psi4Version = float(args.version)
        print(f'Using Psi4 {psi4Version}')
    else:
        if float(args.version) == 0.0:
            psi4Version = 1.5
            print(f'Using Psi4 {psi4Version}')
        else:
            print(f'Psi4 verison {args.version} not recognised')
            psi4Version = 1.5
            print(f'Using Psi4 {psi4Version}')
    
    if psi4Version == 1.3: scratchStr += 'module load psi4/v1.3.2\n\n'
    if psi4Version in [1.4, 1.5]: scratchStr += f'source {project}/apps/psi4-{psi4Version}/activate_psi4.sh\n\n'

    scratchStr += f'export PSIPATH=$PSIPATH:{homePath}/basis\n'
    if args.projectdir == True:
        scratchStr += f'export PSI_SCRATCH="{filePath}/{fileName}"\n'
        scratchStr += f'mkdir "{filePath}/{fileName}"\n'
        scratchStr += f'cp "{filePath}/{fileName}.inp" "{filePath}/{fileName}"\n'
        scratchStr += f'cd "{filePath}/{fileName}"\n'
        scratchStr += f'/usr/bin/time -v psi4 -i "{fileName}.in" -o "{fileName}.out" 2>&1\n\n'
    else:
        scratchStr += f'export PSI_SCRATCH="{scratchDir}"\n\n'
        setupScratch()
        scratchStr += f'/usr/bin/time -v psi4 -i "{fileName}.in" -o "{filePath}/{fileName}.out" 2>&1\n\n'
        copyScratch()

    return

def extractParams(file, program, args):
    with open(file, 'r') as f:
        lines = f.readlines()
    mem = 0
    procs = 0
    
    for line in lines:
        if program == 'gaussian':
            if 'nprocs' in line:
                procs = int(line.split('=')[1])
            if 'mem' in line:
                mem = int(''.join([s for s in list(line.split('=')[1]) if s.isdigit()]))
        if program == 'orca':
            if 'nprocs' in line:
                procs = int(line.split()[1])
            if 'maxcore' in line:
                mem = int(line.split()[1])
        if program == 'psi4':
            if 'set_num_threads' in line:
                procs = int(line.split('(')[1].split(')')[0])
            if 'memory' in line:
                mem = int(''.join([s for s in list(line.split()[1]) if s.isdigit()]))

        if program == 'mopac':
            if 'THREADS' in line:
                for i in line.split():
                    if 'THREADS' in i:
                        procs = int(i.split('=')[1])

    if program == 'orca':
        mem = int((mem*procs)/1024)
    
    mem = args.memory[0] if args.memory[0] != 0 else mem
    if mem == 0:
        print('Memory not identified, using 32GB default')
        mem = 32

    if procs == 0:
        print('Number of cores not identified, using 1 default')
        procs = 1
    
    tpn = args.ntpn[0] if args.ntpn[0] != 0 else procs

    return procs, mem, tpn

def setupTime(args, host):
    global timestring
    global qos

    if args.short == True:
        if host == 'monarch':
            timestring = '24:00:00'
        elif host == 'm3':
            timestring == '00:30:00'
            qos = f'shortq,{args.qos[0]}' if len(args.qos[0]) > 0 else 'shortq'
            part = f'shortq,{args.partition[0]}' if len(args.partition[0]) > 0 else 'shortq'
    elif args.days[0] > 0:
        timestring = f'{args.days[0]*24}:00:00'
    elif args.hours[0] > 0:
        timestring = f'{args.hours[0]:02}:00:00'
    else:
        timestring = f'24:00:00'

    if host == 'monarch':
        part = f'comp,{args.partition[0]}' if len(args.partition[0]) > 0 else 'comp'
        part = f'{part},short' if int(timestring.split(':')[0]) <= 24 else part
        qos = 'partner' if args.normal == False else args.qos[0] if len(args.qos[0]) > 0 else ''
    
    return timestring, part, qos


def main():
    global scratchStr
    global scratchDir
    global fullFilePath
    global filePath
    global fileName
    global copy
    global project
    global homePath
    fileEXTs = {'mop': 'mopac', 'inp': 'orca', 'gjf': 'gaussian', 'com': 'gaussian', '.in': 'psi4'}
    hostname = os.uname().nodename

    if hostname.startswith('monarch'):
        host = 'monarch'
        user = os.getlogin()
        scratch = f'/home/{user}/scratch'
        account = 'p2015120004'
        project = f'/mnt/lustre/projects/{account}'
        homePath = f'{project}/{user}'
    elif hostname.startswith('m3'):
        host = 'm3'
        user = os.getlogin()
        account = 'sn29'
        scratch = f'/home/{user}/{account}_scratch/{user}'
        project = f'/projects/{account}'
        homePath = f'{project}/{user}'
    else:
        print('Cluster not recognised.\nExiting...')
        exit()

    args = read_args()
    for arg in args.files:
        if arg.startswith('-'):
            print(f'{arg} is not a recognised flag.\nExiting..')
            exit() 
    notify = args.notify
    copy = args.copy



    for infile in args.files:
        scratchStr = '#!/bin/bash\n'
        try:
            if os.path.isfile(infile) == False:
                raise Exception()
        except:
            print(f'input file "{infile}" not found.\nNot processing.')
            continue
        fullFilePath = os.path.abspath(infile)
        try:
            program = fileEXTs[infile[-3:]]
        except:
            print('File type not recognised.\nNot processing.')
            continue

        filePath = '/'.join(fullFilePath.split('/')[0:-1])
        fileName = infile.split('/')[-1].split('.')[0]
        scratchDir = f'{scratch}/{fileName}'

        procs, mem, tpn = extractParams(fullFilePath, program, args)
        timestring, part, qos = setupTime(args, host)

        scratchStr += f'#SBATCH --time={timestring}\n'
        scratchStr += f'#SBATCH --ntasks={procs}\n'
        scratchStr += f'#SBATCH --cpus-per-task=1\n'
        scratchStr += f'#SBATCH --ntasks-per-node={tpn}\n'
        scratchStr += f'#SBATCH --mem={mem}GB\n'
        scratchStr += f'#SBATCH --qos={qos}\n' if len(qos) > 0 else ''
        scratchStr += f'#SBATCH --partition={part}\n' if len(part) > 0 else ''
        if args.email == True: scratchStr += f'#SBATCH --mail-type=ALL --mail-user={os.environ["EMAIL"]}\n'
        if hostname == 'm3': scratchStr += f'#SBATCH --account={account}\n' 
        scratchStr += f'\nexport PROJECT="{account}"\n\n'
        

        if notify == True: notifyCall('running')

        if program == 'gaussian': runGaussian()
        if program == 'mopac': runMopac(args)
        if program == 'orca': runOrca(args)
        if program == 'psi4': runPsi4(args)

        if notify == True: notifyCall('finished')

        with open(f'{filePath}/{fileName}.slm', 'w') as slmFile:
            slmFile.write(scratchStr)

        sleep(0.2)

        depcommand = f'-d afterany:{args.dependency}' if args.dependency > 0 else ''
        if args.submit == True:
            command = f'cd "{filePath}" & sbatch {depcommand} "{filePath}/{fileName}.slm"'
            proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, executable='/bin/bash')
            output = proc.stdout.strip('\n')
            if output != "": print(output)
            output = proc.stderr.strip('\n')
            if output != "": print(output)
            if notify == True: notifySubmit()

        if args.touch == True and program != 'mopac': Path(f'{filePath}/{fileName}.out').touch()
    return

if __name__ == "__main__":
    main()