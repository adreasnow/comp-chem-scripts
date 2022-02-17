# Adrea's comp chem scripts (that are worth sharing)

## `compoundScripts/fieldGen`
This tool allows you to generate an electric field based on the grid points surrounding the molecules, and with the help of `plotField.py`, allows you to visualise the fiueld in PyMOL. since Psi4's generation of properties on a grid is serial in nature, I've also parallelised that process.

## `compoundScripts/miniFMO`
This praticular project was a failiure, but attempted ot re-implement the FMO1+2 method in Psi4, using point charge genration of the ESP and optimisation. The process has been documented [on my website](https://adreasnow.com/PhD/Notebook/001/#method-testing) 

## `slmItilities/2slm.sh`
A job submitter for MonARCH and M3 that supports the automatic generation and submisison of `slm` files from ORCA, Psi4, and Gaussian input files. All the slurm settings are fully customisable, but where possible it will automatically detect the settings from the input file itself.

It also supports a few more advanced tricks, like IFTTT notificaitons, file copying, software version selection, dependencies, working form the projects forlder instead of scratch, switching between normal and partner QoS, etc.

## `compoundScripts/orcaIRCMax.py`
Brings the functionality of the Gaussian IRCmax process to ORCA.
* It will create a directory called `scratch` in the location that it's called from, so cd where you want it before you call it
* Takes the `ORCA_ROOT` environment variable, so be sure to source ORCA or load the orca module in your slurm script
* Outputs the resutls to `00-ircmax_results.out`. These include the IRC and IRCmax energies for the specified range
* The IRC job files are prefixed with `irc_` and the IRCmax jobfiles are prefixed with `ircmax_##`.

## `energyExtractors/gsolv.py` and `gsolv-z.py`
These jobs just take ORCA 4/5 output files that have been solvated with CPCM (With or without SMD) and adds on the solvation cavitation and surface charge enrgies into the appropriate Total SCF energy or Gibbs Free Energy. 

`gsolv-z.py` is a modification that prints out the Final SCF energy + ZPVE corrections + solvation corrections.
(yes I could have integrated this into `gsolv.py` with a flag, but I cbf...)

## `energyExtractors/visualise_neb.py`
This does exactly what it says, it takes an ORCA NEB `.interp` file and plots it in a nice neat way that doesn't rely on interpolation through spline fitting.

## `optUtilities/chkoptenergy.py`
Takes the output from an ORCA/Psi4/Gaussian opt job and plots the energy so that you you can see the optimiser progress.