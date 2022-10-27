#! python3
import argparse
def read_args():
    parser = argparse.ArgumentParser(
        description=(
            "Tool to extract xyz files from nwchem outputs"
        )
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
    geomStart = 0
    geomEnd = 0
    xyzList = []
    xyzPosList = []
    for count, line in enumerate(lines):
        if 'start' in line and 'molecule' in line:
            geomStart = count
        if geomStart != 0 and geomEnd == 0:
            splitLine = line.split()
            try:
                test = float(splitLine[1])
                test = float(splitLine[2])
                test = float(splitLine[3])
                geomLen += 1
            except:
                pass

        if 'end' in line and geomLen != 0 and geomStart != 0:
            geomEnd = count

        if 'Geometry "geometry" -> "geometry"' in line and geomLen != 0:
            xyzBuffer = ''
            xyzPosList += [count + 7]
    

    xyzOut = ''
    for xyzPos in xyzPosList:
        try:
            xyzBuffer = ''
            xyzBuffer += f'{geomLen}\n\n'
            for i in range(xyzPos, (xyzPos + geomLen)):
                line = lines[i].split()
                xyzBuffer += f'{line[1]} {float(line[3]): >20.12f} {float(line[4]): >20.12f} {float(line[5]): >20.12f}\n'
            xyzOut += xyzBuffer
        except:
            pass

    if args.out[0] == '':
        outFile = f'{file.split(".")[0]}.xyz'
    else:
        outFile = args.out[0]

    with open(outFile, 'w+') as f:
        f.write(xyzOut)
