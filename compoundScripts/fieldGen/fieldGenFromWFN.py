import psi4
import numpy as np
from fieldGenInput import *
from joblib import Parallel, delayed
from time import sleep

global field

def generatePoints(mol):
    molecularBuffer = globals()['molecularBuffer']
    gridDensity = globals()['gridDensity']

    xList = []
    yList = []
    zList = []
    for atomNum in range(mol.natom()):
        Xa, Ya, Za = np.multiply([mol.x(atomNum), mol.y(atomNum), mol.z(atomNum)], 0.529177)
        xList += [Xa]
        yList += [Ya]
        zList += [Za]
    xList = np.multiply(xList, 10)
    yList = np.multiply(yList, 10)
    zList = np.multiply(zList, 10)
    xStart = int(min(xList))-molecularBuffer
    xEnd = int(max(xList))+molecularBuffer
    yStart = int(min(yList))-molecularBuffer
    yEnd = int(max(yList))+molecularBuffer
    zStart = int(min(zList))-molecularBuffer
    zEnd = int(max(zList))+molecularBuffer

    points = np.array([ [float(x),float(y),float(z) ] for x in range(xStart, xEnd, gridDensity) for y in range(yStart, yEnd, gridDensity) for z in range(zStart, zEnd, gridDensity)])
    points = np.multiply(points, 0.1)
    X, Y, Z = np.split(points, 3, 1)
    return(points, X, Y, Z)

def sphere(Xp, Yp, Zp, Xa, Ya, Za):
    return(np.sqrt(np.add(
                   np.add(np.square(np.subtract(Xa,Xp)),
                          np.square(np.subtract(Ya,Yp))),
                          np.square(np.subtract(Za,Zp)))))

def molCull(mol, X, Y, Z):
    vdwRadiiDict = {'H': 1.20, 'B': 1.92, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'Na': 2.27, 'P': 1.80, 'S': 1.80, 'Cl': 1.75}
    inBoundsList = []
    for atomNum in range(mol.natom()):
        z = mol.flabel(atomNum)
        Xa, Ya, Za = np.multiply([mol.x(atomNum), mol.y(atomNum), mol.z(atomNum)], 0.529177)
        distances = sphere(X, Y, Z, Xa, Ya, Za).flat
        inBoundsList += [np.less_equal(distances, vdwRadiiDict[z]*globals()['radiiScaling'])]
    inBounds = [False for x in range(len(inBoundsList[0]))]
    for i in inBoundsList:
        inBounds = np.logical_or(inBounds, i)
        
    outNucleiList = []
    for atomNum in range(mol.natom()):
        z = mol.flabel(atomNum)
        Xa, Ya, Za = np.multiply([mol.x(atomNum), mol.y(atomNum), mol.z(atomNum)], 0.529177)
        distances = sphere(X, Y, Z, Xa, Ya, Za).flat
        outNucleiList += [np.less_equal(distances, vdwRadiiDict[z]*globals()['vdwScaling'])]
    outNuclei = [False for x in range(len(outNucleiList[0]))]
    for i in outNucleiList:
        outNuclei = np.logical_or(outNuclei, i)

    return(np.logical_xor(outNuclei, inBounds))

def palFieldCompute(mat):
    wfn = psi4.core.Wavefunction.from_file('wfn.npy')
    myesp = psi4.core.ESPPropCalc(wfn)
    psi4mat = psi4.core.Matrix.from_array(mat)
    vecs = myesp.compute_field_over_grid_in_memory(psi4mat).np
    return([vecs, mat])

def calcEField(mol, wfn, file='eField'):
    points, X, Y, Z = generatePoints(mol)
    culled = molCull(mol, X, Y, Z)
    
    culledPoints_X = X[culled].flat
    culledPoints_Y = Y[culled].flat
    culledPoints_Z = Z[culled].flat

    culledPoints = np.column_stack((culledPoints_X, culledPoints_Y, culledPoints_Z))

    numThreads = psi4.get_num_threads()
    lenThread = round(culledPoints.shape[0]/numThreads)
    count = 0
    pointsThreadList = []
    for i in range(numThreads):
        pointsThreadList += [culledPoints[count:count+lenThread]]
        count += lenThread

    if count < culledPoints.shape[0]:
        pointsThreadList += [culledPoints[count:culledPoints.shape[0]-count]]

    wfn.to_file('wfn')

    results = Parallel(n_jobs=numThreads)(delayed(palFieldCompute)(i) for i in pointsThreadList)

    for count, i in enumerate(results):
        if count == 0:
            field = i[0]
            points = i[1]
        else:
            field = np.concatenate((field, i[0]))
            points = np.concatenate((points, i[1]))

    np.save(f'{file}-vecs', field)
    np.save(f'{file}-points', points)

field = []
# e, wfn = psi4.energy(theory, return_wfn=True)
wfn = psi4.core.Wavefunction.from_file('wfn.npy')
molecule = wfn.molecule()
psi4.core.timer_on('Generate eField')
psi4.core.print_out(f'Calculating the electirc field on {psi4.get_num_threads()} threads...')
calcEField(molecule, wfn)
psi4.core.print_out('done')
psi4.core.timer_off('Generate eField')

