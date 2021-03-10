#!/bin/bash -l
# delete slurm files
rm -rf ./slurm*.out

# move gjf files into input folder (if not already in there)
mkdir in
mv ./*.in ./in

# move slrm files into slrm folder
mkdir slm
mv ./*.slm ./slm

# move log files to oit folder
mkdir out
mv ./*.out ./out

rm -rf timer.dat