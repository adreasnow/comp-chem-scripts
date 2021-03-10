#!/bin/bash
# For each file in the input list
for var1 in $@
	do
	var1file=`basename -s .xyz $var1`

	# Check if an alkyl or aromatic structure
	if [[ $var1file == alkyl* ]] || [[ $var1file == aromatic* ]]; then
		PATH1=`readlink -f $var1`

		# For each file in the input list
		for var2 in $@
		do
			var2file=`basename -s .xyz $var2`

			# Check if a cation, anion or metal
			if [[ $var2file == cation* ]] || [[ $var2file == anion* ]] || [[ $var2file == metal* ]]; then
				PATH2=`readlink -f $var2`

				# Set the path to cd back to to
				FOLDER=`pwd -P`

				# Strip just the filename out of the whole path
				FILENAME1=`/bin/basename -s .xyz $PATH1`
				FILENAME2=`/bin/basename -s .xyz $PATH2`

				# Set the name to be used for naming folders and files
				PROJECT="`echo $FILENAME1 | /bin/cut -d'-' -f2`-`echo $FILENAME2 | /bin/cut -d'-' -f2`"


				# Check the charge based on the filename
				if [[ $FILENAME2 == anion* ]]; then
					CHARGE="-1"
					MULT="1"
				elif [[ $FILENAME2 == cation* ]]; then
					CHARGE="1"
					MULT="1"
				elif [[ $FILENAME2 == metal* ]]; then
					CHARGE="2"
					if [[ $PROJECT == *'Pd' ]]; then
						MULT="1"
					elif [[ $PROJECT == *'Ni' ]]; then
						MULT="3"
					fi
				fi

				############################################################ Begin Iterative Script ############################################################
				mkdir $PROJECT


				# Generate the genmer input

				echo "ngen= 10   // The number of configurations expected to be generated. Default: 1" 																				> "./$PROJECT/genmer.ini"
				echo "ngenmust= 0  // The number of configurations must to be generated. Default: 0 (No requirement)"																>> "./$PROJECT/genmer.ini"
				echo "step= 0.1  // Step size to grow monomer from cluster center, larger value leads to faster   calculation but lower accuracy. Default: 0.1" 					>> "./$PROJECT/genmer.ini"
				echo "ishuffle= 0    // 0: Don't shuffle the sequence of monomer types  1: Shuffle the sequence. Default: 0" 														>> "./$PROJECT/genmer.ini"
				echo "imoveclust= 1    // 1: Move geometry center of the constructed clusters to (0,0,0)  0: Keep initial position. Default: 1" 									>> "./$PROJECT/genmer.ini"
				echo "irandom= 1    // 0: Result of each time of execution will be identical  1: Will be different to due use of different random seed in each run. Default: 1" 	>> "./$PROJECT/genmer.ini"
				echo "iradtype= 1    // 0: Use CSD covalent radii to detect contacts  1: Use Bondi vdW radii. Default: 1" 															>> "./$PROJECT/genmer.ini"
				echo "radscale= 0.8  // Scale factor of atomic covalent and vdW radii. Default: 1.0" 																				>> "./$PROJECT/genmer.ini"
				echo "maxemit= 300  // The maximum number of attempts of emitting monomer. Default: 300" 																			>> "./$PROJECT/genmer.ini"
				echo "---- Below are number (may with options) and .xyz file of each type of monomer ----" 																			>> "./$PROJECT/genmer.ini"
				echo "1 rmax 5" 																																					>> "./$PROJECT/genmer.ini"
				echo "$PATH1"																																				>> "./$PROJECT/genmer.ini"
				echo "1 rmax 5" 																																					>> "./$PROJECT/genmer.ini"
				echo "$PATH2"																																				>> "./$PROJECT/genmer.ini"

				# Generate the molclus input
				echo "iprog= 1  // The computational code to invoke. 1: Gaussian, 2: MOPAC, 3: ORCA, 4: xtb, 5: Open Babel"																													> "./$PROJECT/settings.ini"
				echo "ngeom= 0  // Geometries in traj.xyz to be considered. 0: All, n: First n. You can also use e.g. 2,5-8,12-14 to customize range"																						>> "./$PROJECT/settings.ini"
				echo "itask= 0  // Type of task. 0: Optimization, 1: Single point energy, 2: frequency, 3: Optimization with frequency, -1: Composite method (only for Gaussian, e.g. CBS-QB3)"												>> "./$PROJECT/settings.ini"
				echo "ibkout= 1  // When backup output file. 0: Never, 1: All, 2: Successful tasks =3: Failed tasks"																														>> "./$PROJECT/settings.ini"
				echo "distmax= 999  // If distance between any two atoms is larger than this (Angstrom), the geometry will be skipped"																										>> "./$PROJECT/settings.ini"
				echo "ipause= 0  // When pause molclus. 1: Optimization didn't converge (For Gaussian and ORCA), =2: After each cycle, =0: Never pause"																						>> "./$PROJECT/settings.ini"
				echo "freeze= 0  // Index of atoms to be freezed during optimization, e.g. 2,4-8,13-14. If no atom is to be freezed, this option should be set to 0"																		>> "./$PROJECT/settings.ini"
				echo "--- Below for Gaussian ---"																																															>> "./$PROJECT/settings.ini"
				echo "gaussian_path= \"/usr/local/gaussian/g16a03/g16/g16\"  // Command for invoking Gaussian"																																>> "./$PROJECT/settings.ini"
				echo "igaucontinue= 0  // 1: If optimization exceeded the upper number of steps, continue to optimize the last geometry using template2.gjf  0: Don't continue"																>> "./$PROJECT/settings.ini"
				echo "energyterm= \"HF=\" // For itask= 0 or 1, set label for extracting electron energy from archive part of output file, e.g. HF=, MP2=, CCSD(T)=. For itask= -1, set label for extracting thermodynamic quantity"		>> "./$PROJECT/settings.ini"
				echo "ibkchk= 0  // The same as ibkout, but for .chk file"																																									>> "./$PROJECT/settings.ini"
					
				# Generate the gaussian template file 
				echo "%nprocshared=16"														> "./$PROJECT/template.gjf"
				echo "%mem=31GB"															>> "./$PROJECT/template.gjf"
				echo "# M062X/aug-cc-pvdz opt=(maxcyc=200) SCRF=(SMD,solvent=ethanol)"		>> "./$PROJECT/template.gjf"
				echo ""																		>> "./$PROJECT/template.gjf"
				echo "Template file"														>> "./$PROJECT/template.gjf"
				echo ""																		>> "./$PROJECT/template.gjf"
				echo "$CHARGE $MULT"														>> "./$PROJECT/template.gjf"
				echo "[GEOMETRY]"															>> "./$PROJECT/template.gjf"
				echo ""																		>> "./$PROJECT/template.gjf"


				# Generate the slurm job file
				echo "#!/bin/bash -l"																> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --time=24:00:00"														>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --ntasks=16"															>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --cpus-per-task=1"													>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --ntasks-per-node=16"													>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --mem=32GB"															>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --partition=comp,short"												>> "./$PROJECT/$PROJECT.slm"
				echo "#SBATCH --qos=partner"														>> "./$PROJECT/$PROJECT.slm"
				echo ""																				>> "./$PROJECT/$PROJECT.slm"
				echo "module load gaussian/g16a03"													>> "./$PROJECT/$PROJECT.slm"
				echo "export PROJECT=\"p2015120004\""												>> "./$PROJECT/$PROJECT.slm"
				echo "export GAUSS_EXEDIR=/usr/local/gaussian/g16a03/g16"							>> "./$PROJECT/$PROJECT.slm"
				echo "export GAUSS_SCRDIR=\"/home/adreas/scratch/$PROJECT\""						>> "./$PROJECT/$PROJECT.slm"
				echo "export SCRATCHDIR=\"/home/adreas/scratch/$PROJECT\""							>> "./$PROJECT/$PROJECT.slm"
				echo ""																				>> "./$PROJECT/$PROJECT.slm"
				echo "mkdir \"/home/adreas/scratch/$PROJECT\""										>> "./$PROJECT/$PROJECT.slm"
				echo "cd \"$FOLDER/$PROJECT\""														>> "./$PROJECT/$PROJECT.slm"
				echo "/mnt/lustre/projects/p2015120004/apps/molclus/molclus >> \"./$PROJECT.out\""	>> "./$PROJECT/$PROJECT.slm"
				echo ""																				>> "./$PROJECT/$PROJECT.slm"
				echo "rm -rf \"/home/adreas/scratch/$PROJECT\""										>> "./$PROJECT/$PROJECT.slm"

				if [[ $PROJECT == *'Pd' ]] || [[ $PROJECT == *'Ni' ]]; then
					# Generate the gaussian template file 
					echo "%nprocshared=16"														> "./$PROJECT/template.gjf"
					echo "%mem=31GB"															>> "./$PROJECT/template.gjf"
					if [[ $PROJECT == *'Pd' ]]; then
						echo "# M06L/Gen scf=(tight,MaxCycle=300,XQC) opt=(maxcyc=1) SCRF=(SMD,solvent=ethanol)"				>> "./$PROJECT/template.gjf"
					elif [[ $PROJECT == *'Ni' ]]; then
						echo "# UM062X/Gen scf=(tight,MaxCycle=300,XQC) opt=(maxcyc=200) SCRF=(SMD,solvent=ethanol)"			>> "./$PROJECT/template.gjf"
					fi
					echo ""																		>> "./$PROJECT/template.gjf"
					echo "Template file"														>> "./$PROJECT/template.gjf"
					echo ""																		>> "./$PROJECT/template.gjf"
					echo "$CHARGE $MULT"														>> "./$PROJECT/template.gjf"
					echo "[GEOMETRY]"															>> "./$PROJECT/template.gjf"
					echo ""																		>> "./$PROJECT/template.gjf"

				if [[ $PROJECT == *'Pd' ]] || [[ $PROJECT == *'Ni' ]]; then
					if [[ $PROJECT == *'Pd' ]]; then
						echo "Pd 0"																>> "./$PROJECT/template.gjf"
					elif [[ $PROJECT == *'Ni' ]]; then
						echo "Ni 0"																>> "./$PROJECT/template.gjf"
					fi
						echo "Def2QZVP"															>> "./$PROJECT/template.gjf"
					if [[ $PROJECT == 'furan'* ]]; then
						echo "****"																>> "./$PROJECT/template.gjf"
						echo "C H O 0"															>> "./$PROJECT/template.gjf"
						echo "aug-cc-pvdz"														>> "./$PROJECT/template.gjf"
						echo "****"																>> "./$PROJECT/template.gjf"
					elif [[ $PROJECT == 'pyrrole'* ]]; then
						echo "****"																>> "./$PROJECT/template.gjf"
						echo "C H N 0"															>> "./$PROJECT/template.gjf"
						echo "aug-cc-pvdz"														>> "./$PROJECT/template.gjf"
						echo "****"																>> "./$PROJECT/template.gjf"
					else
						echo "****"																>> "./$PROJECT/template.gjf"
						echo "C H 0"															>> "./$PROJECT/template.gjf"
						echo "aug-cc-pvdz"														>> "./$PROJECT/template.gjf"
						echo "****"																>> "./$PROJECT/template.gjf"
					fi
				fi
					echo ""																		>> "./$PROJECT/template.gjf"

				echo "########################################## $PROJECT ##########################################"
				# run genmer and submit to sbatch
				cd ./$PROJECT
				/mnt/lustre/projects/p2015120004/apps/molclus/genmer/genmer
				# /opt/slurm-19.05.4/bin/sbatch "./$PROJECT.slm"
				cd $FOLDER
				fi
			fi
		done
	fi
done




