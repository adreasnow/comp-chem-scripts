#!/bin/bash -l

module load boost/1.62.0-gcc4
module load zlib/1.2.11


HOMEPATH=`pwd -P`
for var in $@
do
	if [ ${var: -4} == ".xyz" ]; then
		FULLFILEPATH=`readlink -f $var`
		FILEPATH=`dirname $FULLFILEPATH`
		FILEPATHSLASH=$FILEPATH/
		FILENAME=`/bin/basename -s .xyz $FULLFILEPATH`

		/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -xk "#p opt m062x/aug-cc-pvdz scf=tight scrf=(cpcm,solvent=ethanol)" -ogjf -O"$FILEPATH/$FILENAME.gjf"


		if [[ $FILENAME == *'high' ]]; then
			sed -i 's/0  2/0 1/' "$FILEPATH/$FILENAME.gjf"
			sed -i 's/*/Cl/' "$FILEPATH/$FILENAME.gjf"

		elif [[ $FILENAME == *'low' ]]; then
			sed -i 's/0  2/0 1/' "$FILEPATH/$FILENAME.gjf"
			sed -i 's/*/Li/' "$FILEPATH/$FILENAME.gjf"
		fi

		printf '%s' $FILEPATH/$FILENAME.chk
		echo -e "%chk=$FILEPATH/$FILENAME.chk\n$(cat "$FILEPATH/$FILENAME.gjf")" > "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%mem=31GB\n/' "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%nprocshared=16\n/' "$FILEPATH/$FILENAME.gjf"

		bash ~/bin/gjf2slm $FILEPATH/$FILENAME.gjf

	fi
done



module unload boost/1.62.0-gcc4
module unload zlib/1.2.11