#! python3
import sys
import os


for file in sys.argv[1:]:
    corrected = []
    corrected_delta_g = []
    charge_correction = 0
    free_energy = 0
    delta_g = 0
    delta_e = 0
    delta_g_count = 0
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
        elif "Final Gibbs free energy" in line:
            delta_g = float(line.split()[5])
        elif "FINAL SINGLE POINT ENERGY" in line:
            delta_e = float(line.split()[4])
        elif "* O   R   C   A *" in line:
            outputfile = True
        if delta_e != 0:
            corrected += [charge_correction + free_energy + delta_e]
            delta_e = 0
        if delta_g != 0:
            del corrected[-1]
            corrected += [charge_correction + free_energy + delta_g]
            corrected_delta_g += [charge_correction + free_energy + delta_g]
            delta_g = 0
            delta_g_count += 1

    if outputfile == True and len(corrected) > 0:
        if delta_g_count == 1:
            print(f"{file.split('/')[-1]} Delta G single")
            print(corrected_delta_g[0])
        elif delta_g_count > 1:
            print(f"{file.split('/')[-1]} Delta G multiple")
            for i in corrected_delta_g:
                print(i)
        else:
            print(f"{file.split('/')[-1]} Delta E")
            for i in corrected:
                print(i)
    else:
        print(f"{file.split('/')[-1]} is not a solvated ORCA output")