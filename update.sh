#! /bin/zsh

echo "----------------------------------- Update Conda ------------------------------------" >> $logfile
conda clean -a -y
conda update --all -y
conda clean -a -y