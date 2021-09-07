# Adrea's comp chem scripts (that are worth sharing)

## `2slm.sh`
A job submitter for MonARCH and M3 that supports the automatic generation and submisison of `slm` files from ORCA, Psi4, and Gaussian input files. All the slurm settings are fully customisable, but where possible it will automatically detect the settings from the input file itself.

It also supports a few more advanced tricks, like IFTTT notificaitons, file copying, software version selection, dependencies, working form the projects forlder instead of scratch, switching between normal and partner QoS, etc.

## `gsolv.py` and `gsolv-z.py`
These jobs just take ORCA 4/5 output files that have been solvated with CPCM (With or without SMD) and adds on the solvation cavitation and surface charge enrgies into the appropriate Total SCF energy or Gibbs Free Energy. 

`gsolv-z.py` is a modification that prints out the Final SCF energy + ZPVE corrections + solvation corrections.
(yes I could have integrated this into `gsolv.py` with a flag, but I cbf...)

## `visualise_neb.py`
This does exactly what it says, it takes an ORCA NEB `.interp` file and plots it in a nice neat way that doesn't rely on interpolation through spline fitting.

## `chkoptenergy.py`
Takes the output from an ORCA/Psi4/Gaussian opt job and plots the energy so that you you can see the optimiser progress.