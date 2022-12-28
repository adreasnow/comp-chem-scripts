#! python3
import subprocess
from tabulate import tabulate


def runbash(command:str) -> list[str]:
    out = subprocess.run(command, shell=True, check=False, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
    return out.stdout.decode().split('\n')[1:-1]


def main() -> None:
    queueOut = runbash("/opt/slurm-20.11.9/bin/squeue -o'%.8T %.4C %q' -u asnow --sort=C")
    runningQueues = {'partner': 0, 'normal': 0}
    pendingQueues = {'partner': {}, 'normal': {}}

    for line in queueOut:
        state, cores, queue = line.split()
        if state == 'RUNNING':
            runningQueues[queue] += int(cores)
        elif state == 'PENDING':
            try:
                pendingQueues[queue][cores] += 1
            except:
                pendingQueues[queue][cores] = 1

    print(f'\nCores used on running jobs:\n---------------------------')
    tableList = [['Queue', '#running', '#total', '#free'], 
                ['partner', runningQueues["partner"], 144, 144-int(runningQueues["partner"])], 
                ['normal', runningQueues["normal"], 144, 144-int(runningQueues["normal"])]]

    print(tabulate(tableList, headers='firstrow'))

    print('\nJobs queued:\n------------')
    tableList = [['Queue', '#cores  ', '#jobs ']]
    for queues in pendingQueues:
        for coreCounts in pendingQueues[queues]:
            tableList += [[queues, coreCounts, pendingQueues[queues][coreCounts]]]

    print(tabulate(tableList, headers='firstrow'))
    print('\n')

    # print(f'Jobs queued:\n\tNormal: {pendingQueues["normal"]}\n\tPartner: {pendingQueues["partner"]}')

if __name__ == "__main__":
    main()