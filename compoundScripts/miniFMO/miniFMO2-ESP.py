import psi4
import numpy as np
from miniFMOInput import *

global rmsd
global chargeTotal
global systemCharge
global numChargePoints

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
    radii = globals()['radii']
    vdwRadiiDict = {'H': 1.20, 'B': 1.92, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'Na': 2.27, 'P': 1.80, 'S': 1.80, 'Cl': 1.75}
    inBoundsList = []
    for atomNum in range(mol.natom()):
        z = mol.flabel(atomNum)
        Xa, Ya, Za = np.multiply([mol.x(atomNum), mol.y(atomNum), mol.z(atomNum)], 0.529177)
        distances = sphere(X, Y, Z, Xa, Ya, Za).flat
        inBoundsList += [np.less_equal(distances, vdwRadiiDict[z]*globals()['radiiScaling']*globals()['vdwScaling'])]
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

def calcESP(mol, wfn):
    points, X, Y, Z = generatePoints(mol)
    culled = molCull(mol, X, Y, Z)
    
    culledPoints_X = X[culled].flat
    culledPoints_Y = Y[culled].flat
    culledPoints_Z = Z[culled].flat

    culledPoints = np.column_stack((culledPoints_X, culledPoints_Y, culledPoints_Z))
    psi4mat = psi4.core.Matrix.from_array(culledPoints)
    
    myesp = psi4.core.ESPPropCalc(wfn)
    charges = myesp.compute_esp_over_grid_in_memory(psi4mat)

    fragcharge = mol.molecular_charge()

    newCharges = np.multiply(charges.np, 1/len(charges.np))

    return(newCharges, culledPoints_X, culledPoints_Y, culledPoints_Z)

class pointCloudToPrint:
    def __init__(self):
        self.chargeCloud = np.array([[0, 0, 0, 0]])
        globals()['systemCharge'] = 0
        globals()['chargeTotal'] = 0
        for i in fragList:
            globals()['systemCharge'] += fragList[i][0].molecular_charge()
        

    def append(self, charges, pointsX, pointsY, pointsZ):
        chargeCloudAdd = np.column_stack((charges, pointsX, pointsY, pointsZ))
        self.chargeCloud = np.concatenate((self.chargeCloud, chargeCloudAdd))

    def write(self, file='chargeCloud'):
        self.chargeCloud = np.delete(self.chargeCloud, (0), axis=0)
        Q, X, Y, Z = np.split(self.chargeCloud, 4, 1)
        globals()['chargeTotal'] = np.sum(Q)
        globals()['numChargePoints'] = len(Q)
        try:
            Qold, Xold, Yold, Zold = np.split(np.load(f'{file}.npy'), 4, 1)
            dQ = np.subtract(Q, Qold)
            dQMat = np.column_stack((dQ, X, Y, Z))
            np.save(f'd{file}', dQMat)
        except:
            pass
        np.save(file, self.chargeCloud)

def rmsdFunc(a, b):
    return(np.sqrt(
        np.divide(
            np.sum(np.square(np.subtract(b, a))),
            len(a)
        )
    ))

def createChargefield(fragList, fragsToInclude=[], new=False):
    charges = []
    fragCharges = []
    chrgfield = psi4.QMMM()
    rmsd = []
    if new == True:
        psi4.core.print_out('\n\nComputing ESP of fragment:\n')
        chargeCloud = pointCloudToPrint()
    for i, frag in enumerate(fragList):
        if i in fragsToInclude:
            if new == True:
                psi4.core.timer_on('createChargefieldFromESP')
                psi4.core.print_out(f'Fragment: {i+1}/{len(fragsToInclude)}\n')
                charges, pointsX, pointsY, pointsZ = calcESP(fragList[frag][0], fragList[frag][1])
                if frag in pointsDict.keys():
                    rmsd += [rmsdFunc(pointsDict[frag][0], charges)]
                fragCharges += [np.sum(charges)]
                pointsDict[frag] = [charges, pointsX, pointsY, pointsZ]
                chargeCloud.append(charges, pointsX, pointsY, pointsZ)
                psi4.core.timer_off('createChargefieldFromESP')
            else:
                charges, pointsX, pointsY, pointsZ = pointsDict[frag]
                charges = np.add(charges, np.divide(globals()['systemCharge']-globals()['chargeTotal'], globals()['numChargePoints']))
            
            for j, charge in enumerate(charges):
                chrgfield.addChargeBohr(charge, pointsX[j], pointsY[j], pointsZ[j])
    if new == True:
        chargeCloud.write()
        fragCharges = np.add(fragCharges, np.divide(globals()['systemCharge']-globals()['chargeTotal'], globals()['numChargePoints']))
        psi4.core.print_out(f'\n\n')
    chrgfield.populateExtern()
    psi4.core.set_global_option_python('EXTERN', chrgfield.extern)
    return(rmsd)

def FMO1init(fragList):
    createChargefield(fragList, [])
    for i in fragList:
        E, wfn = psi4.energy(theory ,return_wfn=True, molecule=fragList[i][0])
        fragList[i] += [wfn]
        
    # calculate the FMO cluster energy
    fragEnergies = []
    for i in fragList:
        fragEnergies += [fragList[i][1].energy()]
    FMOEnergy = np.sum(fragEnergies)
    return(FMOEnergy, fragEnergies)

def FMO1iter(fragList, rmsd):
    # create the new wfn objects in the 3rd array posiiton
    rmsd = createChargefield(fragList, list(range(len(fragList))), new=True)
    for count, i in enumerate(fragList):
        fragnums = list(range(len(fragList)))
        fragnums.remove(count)
        createChargefield(fragList, fragnums)
        E, wfn = psi4.energy(theory ,return_wfn=True, molecule=fragList[i][0])
        fragList[i] += [wfn]
    
    # delete the old wfn objects
    for i in fragList:
        del fragList[i][1]
        
    # calculate the FMO cluster energy
    fragEnergies = []
    for i in fragList:
        fragEnergies += [fragList[i][1].energy()]
    FMOEnergy = np.sum(fragEnergies)
    
    return(FMOEnergy, fragEnergies, rmsd)

def FMO2(fragList):
    createChargefield(fragList, list(range(len(fragList))), new=True)
    FMO2EnergyList = []
    FMO2CalculatedList = []
    for i in fragList:
        for j in fragList:
            if i != j:
                sortedFrags = sorted([i,j])
                if f'{sortedFrags[0]}{sortedFrags[1]}' not in FMO2CalculatedList:
                    molCharge = fragList[i][0].molecular_charge() + fragList[j][0].molecular_charge()
                    geom = f'{molCharge} 1'
                    for frag in [i, j]:
                        for atomNum in range(fragList[frag][0].natom()):
                            A = fragList[frag][0].fsymbol(atomNum)
                            X, Y, Z = np.multiply([fragList[frag][0].x(atomNum), fragList[frag][0].y(atomNum), fragList[frag][0].z(atomNum)], 0.529177249)
                            geom = f"{geom}\n{A} {X} {Y} {Z}"
                    FMO2Mol = psi4.geometry(geom)
                    fragnums = list(range(len(fragList)))
                    fragnums.remove(int(i[3:]))
                    fragnums.remove(int(j[3:]))
                    createChargefield(fragList, fragnums)
                    e = psi4.energy(theory, molecule=FMO2Mol)
                    FMO2EnergyList += [e-fragList[i][1].energy()-fragList[j][1].energy()]
                    write(f"\t {i[3:]}\t{j[3:]}\t{e:14.8f}\t{e-fragList[i][1].energy()-fragList[j][1].energy():14.8f}")
                    FMO2CalculatedList += [f'{sortedFrags[0]}{sortedFrags[1]}']
    return(np.sum(FMO2EnergyList), FMO2EnergyList)
    
def write(logging):
    with open(logfile, 'a') as f:
        f.write(f"{logging}\n")
        
def D3Disp(fragList, fragsToInclude=[]):
    geom = "0 1"
    for i, frag in enumerate(fragList):
        if i in fragsToInclude:
            for j in range(fragList[frag][0].natom()):
                A = fragList[frag][0].fsymbol(j)
                X, Y, Z = np.multiply([fragList[frag][0].x(j), fragList[frag][0].y(j), fragList[frag][0].z(j)], 0.529177249)
                geom = f"{geom}\n{A} {X} {Y} {Z}"
    dispMol = psi4.geometry(geom)
    dispMol.update_geometry()
    disp, array = dispMol.run_dftd3(theory, D3Level)
    return(disp)

# truncate any old log file
with open(logfile, 'w') as f:
    write("MiniFMO Begin!")

# load in the fragments and create molecule objects
fragList = {}
pointsDict = {}
for i, geom in enumerate(fragGeomList):
    geom = f"""{geom}
            nocom
            noreorient"""
    fragList[f'mol{i}'] = [psi4.geometry(geom)]

# Energy Cycle
# run the first step to generate the charges for all the fragments
stepEnergyList = []
stepEnergy, fragEnergies = FMO1init(fragList)
stepEnergyList += [stepEnergy]
dStepEnergy = stepEnergy

write(f" Iter\t   E       \t   ΔE       \t Max Q RMSD \t Max ΔE Frag \t #Frags conv.\n")
write(f"{len(stepEnergyList):3.0f}\t{stepEnergy: 14.8f}\t{dStepEnergy: 3.6e}")

# my fragment of interest
e1 = fragList['mol0'][1].energy()

rmsd = []

maxDFragEnergy = 1
maxQRMSD = 99
fragConvList = [False]

while ( abs(dStepEnergy) >= FMOEConvTol ) or ( abs(maxDFragEnergy) >= FMOEConvTol ) or ( abs(maxQRMSD) >= FMOQConvTol ) or ( np.sum(fragConvList) < len(fragList) ):
    stepEnergy, fragEnergiesNew, rmsd = FMO1iter(fragList, rmsd)
    try:
        maxQRMSD = np.max(rmsd)
    except:
        maxQRMSD = 9.999999
    dFragEnergies = np.subtract(fragEnergiesNew, fragEnergies)
    fragEnergies = fragEnergiesNew
    maxDFragEnergy = np.max(dFragEnergies)
    fragConvList = np.less_equal(np.abs(dFragEnergies), FMOEConvTol)
    stepEnergyList += [stepEnergy]
    dStepEnergy = stepEnergyList[-1]-stepEnergyList[-2]
    write(f"{len(stepEnergyList):3.0f}\t{stepEnergy: 14.8f}\t{dStepEnergy: 3.6e}\t{maxQRMSD: 3.6e}\t{maxDFragEnergy: 3.6e}\t   {np.sum(fragConvList):3.0f}")
write("~~~~~~~~~~~~~~~~~~~~~ FMO1 CONVERGED ~~~~~~~~~~~~~~~~~~~~~\n\n")
# dispCorrection = D3Disp(fragList, fragsToInclude=list(range(len(fragList))))

write(f"\tFinal MiniFMO1 Energy: {stepEnergy:14.8f}")
# write(f"\tDFT-{D3Level} Dispersion Correction: {dispCorrection:14.8f}")
# write(f"\tFinal MiniFMO1 + Dispersion Correction: {dispCorrection+stepEnergy:14.8f}")

write("\n\n I\t E_I (Eh)")
for count, frag in enumerate(fragList):
    write(f" {count}\t{fragList[frag][1].energy():14.8f}")

write("\n")
write("Calculating FMO2 interactions...")
write("\t I\tJ\t   E_IJ (Eh)   \t E_IJ - E_I - E_J (Eh) ")
FMO2Energy, FMO2EnergyList = FMO2(fragList)
write("~~~~~~~~~~~~~~~~~~~~~ FMO2 CONVERGED ~~~~~~~~~~~~~~~~~~~~~\n\n")
write(f"\tMiniFMO2 Correction Energy: {FMO2Energy:14.8f}")
write(f"\tFinal MiniFMO1 + MiniFMO2 Energy: {stepEnergy+FMO2Energy:14.8f}")
# write(f"\tFinal MiniFMO1 + MiniFMO2 + Dispersion Correction: {dispCorrection+stepEnergy+FMO2Energy:14.8f}")
