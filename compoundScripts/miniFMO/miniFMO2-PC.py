import psi4
import numpy as np
from miniFMOInput import *

def createChargefield(fragList, fragsToInclude=[]):
    charges = []
    chrgfield = psi4.QMMM()
    for i, frag in enumerate(fragList):
        if i in fragsToInclude:
            for j in range(fragList[frag][0].natom()):
                Q = np.array(fragList[frag][1].atomic_point_charges())[j]
                X, Y, Z = [fragList[frag][0].x(j), fragList[frag][0].y(j), fragList[frag][0].z(j)]
                chrgfield.addChargeBohr(Q, X, Y, Z)
    chrgfield.populateExtern()
    psi4.core.set_global_option_python('EXTERN', chrgfield.extern)
    return

def FMO1init(fragList):
    createChargefield(fragList, [])
    for i in fragList:
        E, wfn = psi4.energy(theory ,return_wfn=True, molecule=fragList[i][0])
        fragList[i] += [wfn]
        psi4.oeprop(fragList[i][1], chargeTheory)
        
    # calculate the FMO cluster energy
    fragEnergies =[]
    for i in fragList:
        fragEnergies += [fragList[i][1].energy()]
    FMOEnergy = np.sum(fragEnergies)
    return(FMOEnergy, fragEnergies)

def FMO1iter(fragList):
    # create the new wfn objects in the 3rd array posiiton
    for count, i in enumerate(fragList):
        fragnums = list(range(len(fragList)))
        fragnums.remove(count)
        createChargefield(fragList, fragnums)
        E, wfn = psi4.energy(theory ,return_wfn=True, molecule=fragList[i][0])
        fragList[i] += [wfn]
        psi4.oeprop(fragList[i][-1], chargeTheory)
    
    # delete the old wfn objects
    for i in fragList:
        del fragList[i][1]
        
    # calculate the FMO cluster energy
    fragEnergies = []
    for i in fragList:
        fragEnergies += [fragList[i][1].energy()]
    FMOEnergy = np.sum(fragEnergies)
    
    return(FMOEnergy, fragEnergies)

def FMO2(fragList):
    FMO2EnergyList = []
    FMO2CalculatedList = []
    for i in fragList:
        for j in fragList:
            if i != j:
                sortedFrags = sorted([i,j])
                if f'{sortedFrags[0]}{sortedFrags[1]}' not in FMO2CalculatedList:
                    print(i, j)
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
                    print(fragnums)
                    createChargefield(fragList, fragnums)
                    e = psi4.energy(theory, molecule=FMO2Mol)
                    FMO2EnergyList += [e-fragList[i][1].energy()-fragList[j][1].energy()]
                    print(e-fragList[i][1].energy()-fragList[j][1].energy(), e, fragList[i][1].energy(), fragList[j][1].energy())
                    write(f"\t {i[3:]}\t{j[3:]}\t\t{e:14.8f}\t\t{e-fragList[i][1].energy()-fragList[j][1].energy():14.8f}")
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
for i, geom in enumerate(fragGeomList):
    geom = f"""{geom}
            nocom
            noreorient"""
    fragList[f'mol{i}'] = [psi4.geometry(geom)]

# Energy Cycle
# run the first step to generate the Mulliken charges for all the fragments
stepEnergyList = []
stepEnergy, fragEnergies = FMO1init(fragList)
stepEnergyList += [stepEnergy]
dStepEnergy = stepEnergy

write(f" iter\t\t   E (Eh)   \t\t   ΔE (Eh)  \t\t ΔE Frag 1 (Eh) ")
write(f"{len(stepEnergyList):3.0f}\t\t{stepEnergy:14.8f}\t\t{dStepEnergy:14.8f}")

# my fragment of interest
e1 = fragList['mol0'][1].energy()


while abs(dStepEnergy) > FMOConvTol:
    stepEnergy, fragEnergies = FMO1iter(fragList)
    stepEnergyList += [stepEnergy]
    dStepEnergy = stepEnergyList[-1]-stepEnergyList[-2]
    write(f"{len(stepEnergyList):3.0f}\t\t{stepEnergy:14.8f}\t\t{dStepEnergy:14.8f}\t\t{((e1-fragList['mol0'][1].energy())*2625.5):12.8f}")
write("~~~~~~~~~~~~~~~~~~~~~ FMO1 CONVERGED ~~~~~~~~~~~~~~~~~~~~~\n\n")
dispCorrection = D3Disp(fragList, fragsToInclude=list(range(len(fragList))))

write(f"\tFinal MiniFMO1 Energy: {stepEnergy:14.8f}")
write(f"\tDFT-{D3Level} Dispersion Correction: {dispCorrection:14.8f}")
write(f"\tFinal MiniFMO1 + Dispersion Correction: {dispCorrection+stepEnergy:14.8f}")

write("\n\n I\t E_I (Eh)")
for count, frag in enumerate(fragList):
    write(f" {count}\t{fragList[frag][1].energy():14.8f}")

write("\n")
write("Calculating FMO2 interactions...")
write("\t I\tJ\t\t   E_IJ (Eh)   \t\t E_IJ - E_I - E_J (Eh) ")
FMO2Energy, FMO2EnergyList = FMO2(fragList)
write("~~~~~~~~~~~~~~~~~~~~~ FMO2 CONVERGED ~~~~~~~~~~~~~~~~~~~~~\n\n")
write(f"\tMiniFMO2 Correction Energy: {FMO2Energy:14.8f}")
write(f"\tFinal MiniFMO1 + MiniFMO2 Energy: {stepEnergy+FMO2Energy:14.8f}")
write(f"\tFinal MiniFMO1 + MiniFMO2 + Dispersion Correction: {dispCorrection+stepEnergy+FMO2Energy:14.8f}")
