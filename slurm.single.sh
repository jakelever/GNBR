#!/bin/bash
#
#SBATCH --job-name=gnbr_convert
#
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=16G
set -x

python processGNBR.py --entities entities.tsv2 --parti part-i-chemical-disease-path-theme-distributions.txt --partii part-ii-dependency-paths-chemical-disease-sorted-with-themes.txt --outFile gnbr.chemical-disease.tsv

