#! /bin/bash
module load molden/5.7

for var in $@
do
	if [ ${var: -4} == ".out" ]; then
		filename=`basename -s .out $var`
		echo "======================= $filename ======================="

		fullfilepath=`readlink -f $var`

		psi4chk=`cat "$fullfilepath" | grep Psi4 | tr -s ' ' | cut -d' ' -f2 | tail -n 1`
		gauchk=`cat "$fullfilepath" | grep 'This is part of the Gaussian(R)' | cut -d' ' -f7`

		if [[ $psi4chk == 'Psi4' ]]; then
			pcmcheck=`cat $fullfilepath | grep '~~~~~~~~~~ PCMSolver ~~~~~~~~~~' | cut -d' ' -f2 | tail -n1`
			if [[ $pcmcheck == 'PCMSolver' ]]; then
				python ~/bin/psi4pcm2xyz.py $var
			else
				python ~/bin/psi42xyz.py $var
			fi
			filepath=${fullfilepath%.*}
			echo $fullfilepath
			echo "$filepath.xyz"

			molden -l -z "$filepath.xyz"
			rm "$filepath.xyz"

		elif [[ $gauchk == 'Gaussian(R)' ]]; then
			molden -l -z "$fullfilepath"
		fi
	fi
done

module unload molden/5.7