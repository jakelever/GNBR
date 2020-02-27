import argparse
from collections import defaultdict,Counter

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert GNBR data into more compact files for viewing')
	parser.add_argument('--partiis',required=True,type=str,help='Part ii files')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()


	termNames = defaultdict(Counter)
	for partii in args.partiis.split(','):
		print("Loading %s" % partii)
		with open(partii) as inF:
			headers = ['PubMed ID','Sentence number (0 = title)','First entity name, formatted','First entity name, location (characters from start of abstract)','Second entity name, formatted','Second entity name, location','First entity name, raw string','Second entity name, raw string','First entity name, database ID(s)','Second entity name, database ID(s)','First entity type (Chemical, Gene, Disease)','Second entity type (Chemical, Gene, Disease)','Dependency path','Sentence, tokenized']
			for lineno,line in enumerate(inF):
				split = line.strip('\n').split('\t')
				assert len(headers) == len(split)
				row = { h:v for h,v in zip(headers,split) }

				type1 = row['First entity type (Chemical, Gene, Disease)']
				type2 = row['Second entity type (Chemical, Gene, Disease)']

				entity1 = row['First entity name, formatted']
				entity2 = row['Second entity name, formatted']

				id1 = row['First entity name, database ID(s)']
				id2 = row['Second entity name, database ID(s)']

				termNames[(type1,id1)][entity1] += 1
				termNames[(type2,id2)][entity2] += 1

	with open(args.outFile,'w') as outF:
		for (eType,eID),counter in termNames.items():
			sortedCounts = sorted([ (count,name) for name,count in counter.items() ],reverse=True)
			_,topName = sortedCounts[0]

			outData = [eType,eID,topName]
			outF.write("\t".join(outData) + "\n")

