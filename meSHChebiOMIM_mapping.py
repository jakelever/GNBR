import argparse
import os
from collections import defaultdict

if __name__ == '__main__':
	parser = argparse.ArgumentParser('Get MeSH mapping from ID to name')
	parser.add_argument('--meshDir',required=True,type=str,help='Input directory of MeSH ASCII bin files')
	parser.add_argument('--omimTitles',required=True,type=str,help='Titles file from OMIM')
	parser.add_argument('--chebiNames',required=True,type=str,help='Names file from CHEBI')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()

	files = sorted([ f for f in os.listdir(args.meshDir) if f[0] in ['c','d'] and f.endswith('.bin') ])

	mapping = {}
	with open(args.omimTitles) as f:
		for line in f:
			if line.startswith('#'):
				continue
			split = line.strip('\n').split('\t')
			omim_id = int(split[1])
			name = " ".join(w.capitalize() for w in split[2].lower().split())
			mapping["OMIM:%d" % omim_id] = name

	with open(args.chebiNames) as f:
		header = f.readline()
		for line in f:
			split = line.strip('\n').split('\t')
			chebi_id = int(split[0])
			chebi_compound_id = int(split[1])
			name = split[4]
			mapping["CHEBI:%d" % chebi_compound_id] = name

	for filename in files:
		print(filename)
		with open(os.path.join(args.meshDir,filename)) as f:
			currentRecord = defaultdict(list)
			for line in f:
				line = line.strip('\n')
				if line == '*NEWRECORD':
					if 'UI' in currentRecord and ('NM' in currentRecord or 'MH' in currentRecord):
						assert len(currentRecord['UI']) == 1
						assert len(currentRecord['NM']) == 1 or len(currentRecord['MH']) == 1

						if len(currentRecord['NM']) == 1:
							mapping[currentRecord['UI'][0]] = currentRecord['NM'][0]
						elif len(currentRecord['MH']) == 1:
							mapping[currentRecord['UI'][0]] = currentRecord['MH'][0]


					currentRecord = defaultdict(list)
				elif '=' in line:
					equalsIndex = line.index('=')
					name = line[:equalsIndex].strip()
					value = line[(equalsIndex+1):].strip()
					currentRecord[name].append(value)

			if 'UI' in currentRecord and ('NM' in currentRecord or 'MH' in currentRecord):
				assert len(currentRecord['UI']) == 1
				assert len(currentRecord['NM']) == 1 or len(currentRecord['MH']) == 1

				if len(currentRecord['NM']) == 1:
					mapping[currentRecord['UI'][0]] = currentRecord['NM'][0]
				elif len(currentRecord['MH']) == 1:
					mapping[currentRecord['UI'][0]] = currentRecord['MH'][0]
		#break

	with open(args.outFile,'w') as outF:
		for UI in sorted(mapping.keys()):
			outF.write("%s\t%s\n" % (UI,mapping[UI]))

