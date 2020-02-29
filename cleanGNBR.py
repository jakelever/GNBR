import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Clean up the IDs and entity names of the processed GNBR data')
	parser.add_argument('--gnbr',required=True,type=str,help='GNBR')
	parser.add_argument('--genesAndTaxa',required=True,type=str,help='Genes mapped to taxa and symbols')
	parser.add_argument('--meshChebiOMIMMappings',required=True,type=str,help='MeSH/CHEBI/OMIM IDs mapped to terms')
	parser.add_argument('--outFile',required=True,type=str,help='Output')
	args = parser.parse_args()

	print("Loading gene and taxa...")
	geneInfo = {}
	with open(args.genesAndTaxa) as f:
		for line in f:
			gene_id,gene_name,tax_id,tax_name = line.strip('\n').split('\t')
			gene_id = int(gene_id)
			tax_id = int(tax_id)

			geneInfo[gene_id] = (gene_name,tax_id,tax_name)

	print("Loading MeSH...")
	meshChebiOMIM = {}
	with open(args.meshChebiOMIMMappings) as f:
		for line in f:
			concept_id,term = line.strip('\n').split('\t')
			meshChebiOMIM[concept_id] = term

	print("Processing GNBR...")
	with open(args.gnbr) as f, open(args.outFile,'w') as outF:
		# GNBR.tsv
		#outData = [ theme, percentile, row['PubMed ID'],row['First entity type (Chemical, Gene, Disease)'],row['First entity name, database ID(s)'],name1,row['Second entity type (Chemical, Gene, Disease)'],row['Second entity name, database ID(s)'],name2,sentence ]
		#outF.write("\t".join(headers) + "\n")
	
		for lineno,line in enumerate(f):
			split = line.strip('\n').split('\t')
			theme,percentile,pmid,type1,id1,name1,type2,id2,name2,sentence = split

			if id1 == 'null' or id2 == 'null':
				print("DROP: null")
				continue

			species = []
			if type1 == 'Gene':
				gene_ids = [ int(g.split('(')[0].strip()) for g in id1.split(';') ]
				gene_ids = [ g for g in gene_ids if g in geneInfo ]
				if len(gene_ids) == 0:
					print("DROP: gene_ids 1", id1)
					continue

				#id1 = ",".join(map(str(gene_ids)))
				idsWithTax = []
				for gene_id in gene_ids:
					tax_id = geneInfo[gene_id][1]
					if tax_id == 9606:
						idsWithTax.append(str(gene_id))
					else:
						idsWithTax.append("%d (tax:%d)" % (gene_id,tax_id))
				id1 = ",".join(idsWithTax)

				name1 = "|".join( sorted(set( [ geneInfo[g][0] for g in gene_ids ] ) ) )
				species += [ geneInfo[g][2] for g in gene_ids ]
			else:
				concept_ids = [ concept_id.replace('MESH:','') for concept_id in id1.split('|') ]
				concept_ids = sorted([ concept_id for concept_id in concept_ids if concept_id in meshChebiOMIM ])
				if len(concept_ids) == 0:
					print("DROP: concept_ids 1", id1)
					continue

				id1 = ",".join(concept_ids)
				name1 = "|".join( [ meshChebiOMIM[concept_id] for concept_id in concept_ids ] )
				
			if type2 == 'Gene':
				gene_ids = [ int(g.split('(')[0].strip()) for g in id2.split(';') ]
				gene_ids = [ g for g in gene_ids if g in geneInfo ]
				if len(gene_ids) == 0:
					print("DROP: gene_ids 2", id2)
					continue

				idsWithTax = []
				for gene_id in gene_ids:
					tax_id = geneInfo[gene_id][1]
					if tax_id == 9606:
						idsWithTax.append(str(gene_id))
					else:
						idsWithTax.append("%d (tax:%d)" % (gene_id,tax_id))
				id2 = ",".join(idsWithTax)

				name2 = "|".join( sorted(set( [ geneInfo[g][0] for g in gene_ids ] ) ) )
				species += [ geneInfo[g][2] for g in gene_ids ]
			else:
				concept_ids = [ concept_id.replace('MESH:','') for concept_id in id2.split('|') ]
				concept_ids = sorted([ concept_id for concept_id in concept_ids if concept_id in meshChebiOMIM ])
				if len(concept_ids) == 0:
					print("DROP: concept_ids 1", id2)
					continue

				id2 = ",".join(concept_ids)
				name2 = "|".join( [ meshChebiOMIM[concept_id] for concept_id in concept_ids ] )

			species = sorted(set(species))
			if len(species) == 0:
				speciesText = 'n/a'
			elif len(species) == 1:
				speciesText = species[0]
			else:
				speciesText = 'mixed'

			outData = [theme,percentile,pmid,type1,id1,name1,type2,id2,name2,speciesText,sentence]

			outF.write("\t".join(outData) + "\n")

			#if lineno > 2000:
			#	break
	print("Complete.")


