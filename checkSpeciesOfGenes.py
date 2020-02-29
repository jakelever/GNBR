import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Check the species of genes from GNBR data')
	parser.add_argument('--geneIDs',required=True,type=str,help='All the gene IDs in GNBR')
	parser.add_argument('--ncbiGeneInfo',required=True,type=str,help='Uncompressed version of NCBI gene info file')
	parser.add_argument('--ncbiGeneHistory',required=True,type=str,help='Uncompressed version of NCBI gene history file')
	parser.add_argument('--taxonomyNames',required=True,type=str,help='names.dmp file from NCBI taxonomy taxdmp')
	parser.add_argument('--taxonomyMerged',required=True,type=str,help='merged.dmp file from NCBI taxonomy taxdmp')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()

	print("Loading taxonomy names")
	species = {}
	with open(args.taxonomyNames) as f:
		for line in f:
			split = [ s.strip() for s in line.strip('\n').split('|') ]
			if split[3] == 'scientific name':
				tax_id = int(split[0])
				name = split[1]
				species[tax_id] = name

			#if 9606 in species:
			#	break

	print("Loading taxonomy merges")
	with open(args.taxonomyMerged) as f:
		for line in f:
			split = [ s.strip() for s in line.strip('\n').split('|') ]
			
			old_taxa_id = int(split[0])
			new_taxa_id = int(split[1])

			if new_taxa_id in species:
				species[old_taxa_id] = species[new_taxa_id]

	print("Loading NCBI genes")
	geneToSpeciesID = {}
	with open(args.ncbiGeneInfo) as f:
		headers = f.readline()
		for line in f:
			split = line.strip('\n').split('\t')
			tax_id = int(split[0])
			gene_id = int(split[1])
			geneToSpeciesID[gene_id] = tax_id
			#assert tax_id in species, "Couldn't find taxa_id=%d for gene_id=%d" % (tax_id,gene_id)

	print("Loading NCBI gene history")
	renaming = {}
	discontinued = set()
	with open(args.ncbiGeneHistory) as f:
		headers = f.readline()
		for line in f:
			split = line.strip('\n').split('\t')

			old_gene_id = int(split[2])
			if split[1] == '-':
				discontinued.add(old_gene_id)
			else:
				gene_id = int(split[1])
				renaming[old_gene_id] = gene_id
		

	print("Processing GNBR data")
	with open(args.geneIDs) as f, open(args.outFile,'w') as outF:
		for line in f:
			if line.strip('\n') == 'null':
				continue

			gene_ids = [ int(g.split('(')[0]) for g in line.strip('\n').split(';') ]
			gene_ids = [ renaming[g] if g in renaming else g for g in gene_ids ]

			hasInvalidIDs = any( not g in geneToSpeciesID for g in gene_ids )
			if hasInvalidIDs:
				continue

			for g in gene_ids:
				assert g in geneToSpeciesID, "Couldn't find gene_id=%d" % g

			matched_species = [ geneToSpeciesID[g] for g in gene_ids ]
			matched_species = sorted(set(matched_species))
			for s in matched_species:
				assert s in species, "Couldn't find taxa_id=%d" % s
			species_names = [ species[s] for s in matched_species ]

			outData = [ ",".join(map(str,gene_ids)), ",".join(map(str,matched_species)), ",".join(map(str,species_names)), len(matched_species) == 1 ]
			outF.write("\t".join(map(str,outData)) + "\n")
