#!/bin/bash -l

module load boost/1.62.0-gcc4
module load zlib/1.2.11


HOMEPATH=`pwd -P`
for var in $@
do
	if [ ${var: -4} == ".xyz" ]; then
		FULLFILEPATH=`readlink -f $var`
		FILEPATH=`dirname $FULLFILEPATH`
		FILENAME=`/bin/basename -s .xyz $FULLFILEPATH`

		/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -xk "#p opt/aug-cc-pvtz scf=tight scrf=(SMD,solvent=ethanol)" -ogjf -O"$FILEPATH/$FILENAME.gjf"

		sed -i "1s/^/%chk=$FILENAME.chk\n/" "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%mem=31GB\n/' "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%nprocshared=16\n/' "$FILEPATH/$FILENAME.gjf"

	fi
done



module unload boost/1.62.0-gcc4
module unload zlib/1.2.11