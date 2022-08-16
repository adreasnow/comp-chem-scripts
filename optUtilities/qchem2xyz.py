#! python3
import argparse
def read_args():
    parser = argparse.ArgumentParser(
        description=(
            "Slurm script importer for MonARCH/M3"
        )
    )
    parser.add_argument(
        "-f",
        "--first",
        help='take the first n atoms from the xyz',
        nargs=1,
        default=[0],
        type=int,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--out",
        help='optional output file path/name.xyz',
        nargs=1,
        default=[''],
        type=str,
        required=False,
    )
    parser.add_argument(
        'files', 
        nargs=argparse.REMAINDER
    )
    return parser.parse_args()

args = read_args()

for file in args.files:
    with open(file, 'r') as f:
        lines = f.readlines()

    geomLen = 0
    xyzList = []
    xyzPosList = []
    for count, line in enumerate(lines):
        if '$molecule' in line:
            geomStart = count
        if '$end' in line and geomLen == 0:
            geomEnd = count
            geomLen = geomEnd-geomStart-2

        if 'New Cartesian Coordinates Obtained' in line and geomLen != 0:
            xyzBuffer = ''
            xyzPosList += [count + 7]

        if ' LBFGS Step ' in line and geomLen != 0:
            xyzBuffer = ''
            xyzPosList += [count + 6]

    if args.first != [0]:
        geomLen = args.first[0]

    xyzOut = ''
    for xyzPos in xyzPosList:
        try:
            xyzBuffer = ''
            xyzBuffer += f'{geomLen}\n\n'
            for i in range(xyzPos, (xyzPos + geomLen)):
                line = lines[i].split()
                xyzBuffer += f'{line[1]} {float(line[2]): >20.12f} {float(line[3]): >20.12f} {float(line[4]): >20.12f}\n'
            xyzOut += xyzBuffer
        except:
            pass

    if args.out[0] == '':
        outFile = f'{file.split(".")[0]}.xyz'
    else:
        outFile = args.out[0]

    with open(outFile, 'w+') as f:
        f.write(xyzOut)
