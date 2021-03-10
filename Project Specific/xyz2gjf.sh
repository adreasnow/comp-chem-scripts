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

		if [[ $FILENAME == *'Pd' ]]; then
			/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -xk "#p HF/Gen scf=(tight,MaxCycle=300,XQC) pop=(full,nbo)" -ogjf -O"$FILEPATH/$FILENAME.gjf"
		elif [[ $FILENAME == *'Ni' ]]; then
			/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -xk "#p UHF/Gen scf=(tight,MaxCycle=300,XQC) pop=(full,nbo)" -ogjf -O"$FILEPATH/$FILENAME.gjf"
		else
			/mnt/lustre/projects/p2015120004/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -xk "#p HF/aug-cc-pvtz scf=tight pop=(full,nbo)" -ogjf -O"$FILEPATH/$FILENAME.gjf"
		fi


		if [[ $FILENAME == *'Pd' ]] || [[ $FILENAME == *'Ni' ]]; then
			if [[ $FILENAME == *'Pd' ]]; then
				echo "Pd 0"																>> "$FILEPATH/$FILENAME.gjf"
			elif [[ $FILENAME == *'Ni' ]]; then
				echo "Ni 0"																>> "$FILEPATH/$FILENAME.gjf"
			fi
				echo "Def2QZVP"															>> "$FILEPATH/$FILENAME.gjf"
			if [[ $FILENAME == 'furan'* ]]; then
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
				echo "C H O 0"															>> "$FILEPATH/$FILENAME.gjf"
				echo "aug-cc-pvdz"														>> "$FILEPATH/$FILENAME.gjf"
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
			elif [[ $FILENAME == 'ethane'* ]] || [[ $FILENAME == 'ethyne'* ]] || [[ $FILENAME == 'ethene'* ]] || [[ $FILENAME == 'benzene'* ]]; then
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
				echo "C H 0"															>> "$FILEPATH/$FILENAME.gjf"
				echo "aug-cc-pvdz"														>> "$FILEPATH/$FILENAME.gjf"
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
			elif [[ $FILENAME == 'pyrrole'* ]]; then
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
				echo "C H N 0"															>> "$FILEPATH/$FILENAME.gjf"
				echo "aug-cc-pvdz"														>> "$FILEPATH/$FILENAME.gjf"
				echo "****"																>> "$FILEPATH/$FILENAME.gjf"
			fi
		fi



		if [[ $FILENAME == *'BF2(CF3)2' ]] || [[ $FILENAME == *'BF4' ]] || [[ $FILENAME == *'C(CN)3' ]] || [[ $FILENAME == *'N(SOOCF3)2' ]] || [[ $FILENAME == *'Cl' ]] || [[ $FILENAME == *'N(NC)2' ]] || [[ $FILENAME == *'tempo' ]]; then
			sed -i 's/0  2/-1 1/' "$FILEPATH/$FILENAME.gjf"
		elif [[ $FILENAME == *'C1MPyr' ]] || [[ $FILENAME == *'ImidMe2' ]] || [[ $FILENAME == *'NMe4' ]] || [[ $FILENAME == *'PMe4' ]] || [[ $FILENAME == *'Na' ]] || [[ $FILENAME == *'Li' ]]; then
			sed -i 's/0  2/1 1/' "$FILEPATH/$FILENAME.gjf"
		elif [[ $FILENAME == *'Pd' ]]; then
			sed -i 's/0  2/2 1/' "$FILEPATH/$FILENAME.gjf"
		elif [[ $FILENAME == *'Ni' ]]; then
			sed -i 's/0  1/2 3/' "$FILEPATH/$FILENAME.gjf"
		fi

		sed -i "1s/^/%chk=$FILENAME.chk\n/" "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%mem=31GB\n/' "$FILEPATH/$FILENAME.gjf"
		sed -i '1s/^/%nprocshared=16\n/' "$FILEPATH/$FILENAME.gjf"

	fi
done



module unload boost/1.62.0-gcc4
module unload zlib/1.2.11