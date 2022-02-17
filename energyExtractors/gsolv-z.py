#! python3
import sys
import os


for file in sys.argv[1:]:
    corrected = []
    corrected_zpve = []
    charge_correction = 0
    free_energy = 0
    zpve = 0
    delta_e = 0
    delta_e_last = 0
    zpve_count = 0
    outputfile = False

    file = os.path.abspath(file)
    with open(file, "r") as f:
        contents = f.readlines()
    for line in contents:
        if "Charge-correction" in line:
            charge_correction = float(line.split()[2])
        elif "Free-energy (cav+disp)" in line:
            if line.split()[3] == "This":
                free_energy = 0
            else:
                free_energy = float(line.split()[3])
        elif "Total correction" in line:
            zpve = float(line.split()[2])
        elif "FINAL SINGLE POINT ENERGY" in line:
            delta_e = float(line.split()[4])
        elif "* O   R   C   A *" in line:
            outputfile = True
        if delta_e != 0:
            corrected += [charge_correction + free_energy + delta_e]
            delta_e_last = delta_e
            delta_e = 0
        if zpve != 0:
            del corrected[-1]
            corrected += [charge_correction + free_energy + zpve + delta_e_last]
            corrected_zpve += [charge_correction + free_energy + zpve + delta_e_last]
            zpve = 0
            zpve_count += 1

    if outputfile == True and len(corrected) > 0:
        if zpve_count == 1:
            print(f"{file.split('/')[-1]} Delta E + ZPVE single")
            print(corrected_zpve[0])
        elif zpve_count > 1:
            print(f"{file.split('/')[-1]} Delta E + ZPVE multiple")
            for i in corrected_zpve:
                print(i)
        else:
            print(f"{file.split('/')[-1]} Delta E")
            for i in corrected:
                print(i)
    else:
        print(f"{file.split('/')[-1]} is not a solvated ORCA output")