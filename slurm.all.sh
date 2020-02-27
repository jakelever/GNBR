#!/bin/bash
#
#SBATCH --job-name=gnbr_convert
#
#SBATCH --time=72:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=10G
#SBATCH --qos long
set -x

for assoc in "chemical-disease" "chemical-gene" "gene-disease" "gene-gene"
do
	python processGNBR.py --entities entities.tsv2 --parti part-i-$assoc-path-theme-distributions.txt --partii part-ii-dependency-paths-$assoc-sorted-with-themes.txt --outFile gnbr.$assoc.tsv
done
