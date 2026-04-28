#!/usr/bin/bash
#SBATCH -J save_data    # Job name
#SBATCH -p all          # job partition
#SBATCH -N 1            # Run all processes on a single node	
#SBATCH -c 1            # cores per MPI rank
#SBATCH -n 32           # Run a single task
#SBATCH -o save_data.out  # output file
#SBATCH -e save_data.err  # error file
#SBATCH --nodelist=mogamd

#python save_wind_preci_data.py
#python save_CAE_data.py
python conv_dataset.py
