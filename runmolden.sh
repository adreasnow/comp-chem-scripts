#!/bin/bash -l
module load molden/5.7
molden -l -z $1 
module unload molden/5.7