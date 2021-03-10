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

		/projects/sn29/apps/openbabel-3.0.0/bin/obabel -ixyz "$FULLFILEPATH" -oxyz -O"$FILEPATH/$FILENAME.int.xyz" --separate

		echo "memory 63 GB"															> "$FILEPATH/$FILENAME.in"
		echo "set_num_threads(16)"														>> "$FILEPATH/$FILENAME.in"

		if [[ $FILENAME == *'Pd' ]] || [[ $FILENAME == *'Ni' ]]; then
			echo "basis {"																>> "$FILEPATH/$FILENAME.in"
			echo "   assign aug-cc-pvdz"												>> "$FILEPATH/$FILENAME.in"

			if [[ $FILENAME == *'Pd' ]]; then
				echo "   assign Pd def2-qzvp"											>> "$FILEPATH/$FILENAME.in"
			elif [[ $FILENAME == *'Ni' ]]; then
				echo "   assign Ni def2-qzvp"											>> "$FILEPATH/$FILENAME.in"
			fi

			echo "}"																	>> "$FILEPATH/$FILENAME.in"

		else
				echo "set basis aug-cc-pvdz"											>> "$FILEPATH/$FILENAME.in"

		fi

		echo "molecule {"																>> "$FILEPATH/$FILENAME.in"
		echo "0 1"																		>> "$FILEPATH/$FILENAME.in"
		
		if [[ $FILENAME == *'Na' ]] || [[ $FILENAME == *'Li' ]] || [[ $FILENAME == *'Ni' ]] || [[ $FILENAME == *'Pd' ]]; then
			if [[ $FILENAME == 'furan'* ]]; then
				NLINES1="9"
			elif [[ $FILENAME == 'pyrrole'* ]]; then
				NLINES1="10"
			elif [[ $FILENAME == 'benzene'* ]]; then
				NLINES1="12"
			elif [[ $FILENAME == 'ethane'* ]]; then
				NLINES1="8"
			elif [[ $FILENAME == 'ethyne'* ]]; then
				NLINES1="4"
			elif [[ $FILENAME == 'ethene'* ]]; then
				NLINES1="6"
			fi
			cat "$FILEPATH/$FILENAME.xyz"| grep "Energy" -A $NLINES1 | tail -n $NLINES1 | sed 's/^/    /'		>> "$FILEPATH/$FILENAME.in"
		else
			NLINES1=`cat "$FILEPATH/$FILENAME.int.xyz"| grep "#1" -B 1 | sed -n '1p'`
			cat "$FILEPATH/$FILENAME.int.xyz"| grep "#1" -A $NLINES1 | tail -n $NLINES1 | sed 's/^/    /'		>> "$FILEPATH/$FILENAME.in"
		fi

		if [[ $FILENAME == *'BF2(CF3)2' ]] || [[ $FILENAME == *'BF4' ]] || [[ $FILENAME == *'C(CN)3' ]] || [[ $FILENAME == *'N(SOOCF3)2' ]] || [[ $FILENAME == *'Cl' ]] || [[ $FILENAME == *'N(NC)2' ]] || [[ $FILENAME == *'tempo' ]]; then
			CHARGE="-1"
		elif [[ $FILENAME == *'C1MPyr' ]] || [[ $FILENAME == *'ImidMe2' ]] || [[ $FILENAME == *'NMe4' ]] || [[ $FILENAME == *'PMe4' ]] || [[ $FILENAME == *'Na' ]] || [[ $FILENAME == *'Li' ]]; then
			CHARGE="1"
		elif [[ $FILENAME == *'Pd' ]] || [[ $FILENAME == *'Ni' ]]; then
			CHARGE="2"
		fi

		echo "--"																		>> "$FILEPATH/$FILENAME.in"
		echo "$CHARGE 1"																>> "$FILEPATH/$FILENAME.in"

		if [[ $FILENAME == *'Pd' ]] || [[ $FILENAME == *'Ni' ]] || [[ $FILENAME == *'Na' ]] || [[ $FILENAME == *'Li' ]]; then
			echo "    `tail -n 1 "$FILEPATH/$FILENAME.xyz"`"							>> "$FILEPATH/$FILENAME.in"
		else
			NLINES2=`cat "$FILEPATH/$FILENAME.int.xyz"| grep "#2" -B 1 | sed -n '1p'`
			cat "$FILEPATH/$FILENAME.int.xyz"| grep "#2" -A $NLINES2 | tail -n $NLINES2 | sed 's/^/    /'		>> "$FILEPATH/$FILENAME.in"
		fi

		rm "$FILEPATH/$FILENAME.int.xyz"

		echo "}"																		>> "$FILEPATH/$FILENAME.in"
		echo ""																			>> "$FILEPATH/$FILENAME.in"
		echo "set scf {"																>> "$FILEPATH/$FILENAME.in"
		echo "    maxiter 500"															>> "$FILEPATH/$FILENAME.in"
		echo "    soscf   true"															>> "$FILEPATH/$FILENAME.in"
		echo "}"																		>> "$FILEPATH/$FILENAME.in"
		echo ""																			>> "$FILEPATH/$FILENAME.in"
		echo "set sapt {"																>> "$FILEPATH/$FILENAME.in"
		echo "    print   1"															>> "$FILEPATH/$FILENAME.in"
		echo "}"																		>> "$FILEPATH/$FILENAME.in"
		echo ""																			>> "$FILEPATH/$FILENAME.in"
		echo "energy('sapt2+-ct')"														>> "$FILEPATH/$FILENAME.in"
		echo ""																			>> "$FILEPATH/$FILENAME.in"


	fi
done

module unload boost/1.62.0-gcc4
module unload zlib/1.2.11
