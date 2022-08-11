#! python3
import sys


for file in sys.argv[1:]:
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

	xyzBuffer = ''
	for xyzPos in xyzPosList:
		xyzBuffer += f'{geomLen}\n\n'
		for i in range(xyzPos, (xyzPos + geomLen)):
			line = lines[i]
			xyzBuffer += f'{line.split()[1]} {float(line.split()[2]): >20.12f} {float(line.split()[3]): >20.12f} {float(line.split()[4]): >20.12f}\n'

	with open(f'{file.split(".")[0]}.xyz', 'w+') as f:
		f.write(xyzBuffer)





