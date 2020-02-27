import argparse
import html
from scipy import stats
from collections import defaultdict

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Convert GNBR data into more compact files for viewing')
	parser.add_argument('--entities',required=True,type=str,help='Entity mappings')
	parser.add_argument('--parti',required=True,type=str,help='Part i file for relation')
	parser.add_argument('--partii',required=True,type=str,help='Part i file for relation')
	parser.add_argument('--outFile',required=True,type=str,help='Output file')
	args = parser.parse_args()

	print("Reading entities...")
	entityNames = {}
	with open(args.entities) as f:
		for line in f:
			eType,eID,eName = line.strip('\n').split('\t')
			entityNames[(eType,eID)] = eName

	print("Collecting scores...")
	allScores = defaultdict(list)
	pathToTheme = {}
	with open(args.parti) as f:
		headers = f.readline().strip('\n').split('\t')
		for line in f:
			split = line.strip('\n').split('\t')
			assert len(headers) == len(split)
			#row = { h:v for h,v in zip(header,line.strip('\n').split('\t') }
			scores = [ (float(score),theme) for theme,score in zip(headers[1:],split[1:]) ]

			for theme,score in zip(headers[1:],split[1:]):
				if not ".ind" in theme:
					allScores[theme].append(float(score))

	print("Calculating percentile ranks for each dependency path...")
	allPercentiles = {}
	for theme in allScores:
		percentiles = stats.rankdata(allScores[theme],"average") / len(allScores[theme])
		allPercentiles[theme] = percentiles
	
	print("Assigning percentiles to dependency path...")
	with open(args.parti) as f:
		headers = f.readline().strip('\n').split('\t')
		themes = [ h for h in headers[1:] if not ".ind" in h ]
		for i,line in enumerate(f):
			split = line.strip('\n').split('\t')
			assert len(headers) == len(split)
			#row = { h:v for h,v in zip(header,line.strip('\n').split('\t') }
			#scores = [ (float(score),theme) for theme,score in zip(headers[1:],split[1:]) ]
			
			percentiles = [ (allPercentiles[theme][i],theme) for theme in themes ]

			#percentiles = [ (stats.percentileofscore(allScores[theme],score),theme) for score,theme in scores ]
			

			path = split[0].lower()

			percentiles = sorted(percentiles, reverse=True)
			topPercentile,topTheme = percentiles[0]
			#if topScore > 0.8:
			pathToTheme[path] = (topTheme,topPercentile)
			#print(path, topTheme, topPercentile)
			#assert False

	print("Matching dependency path classifications with sentences...")
	with open(args.partii) as inF, open(args.outFile,'w') as outF:
		headers = ['PubMed ID','Sentence number (0 = title)','First entity name, formatted','First entity name, location (characters from start of abstract)','Second entity name, formatted','Second entity name, location','First entity name, raw string','Second entity name, raw string','First entity name, database ID(s)','Second entity name, database ID(s)','First entity type (Chemical, Gene, Disease)','Second entity type (Chemical, Gene, Disease)','Dependency path','Sentence, tokenized']
		for lineno,line in enumerate(inF):
			split = line.strip('\n').split('\t')
			assert len(headers) == len(split)
			row = { h:v for h,v in zip(headers,split) }

			path = row['Dependency path'].lower()
			if path in pathToTheme:
				theme,percentile = pathToTheme[path]

				sentence = row['Sentence, tokenized']

				text1 = row['First entity name, formatted']
				text2 = row['Second entity name, formatted']

				raw1 = row['First entity name, raw string']
				raw2 = row['Second entity name, raw string']

				sentence = html.escape(sentence)
				sentence = sentence.replace(text1,'<b>%s</b>' % raw1)
				sentence = sentence.replace(text2,'<b>%s</b>' % raw2)
				sentence = sentence.replace('-LRB-','(').replace('-RRB-',')')

				if row['First entity name, database ID(s)'] == 'null':
					continue
				elif row['Second entity name, database ID(s)'] == 'null':
					continue

				name1 = entityNames[(row['First entity type (Chemical, Gene, Disease)'],row['First entity name, database ID(s)'])]
				name2 = entityNames[(row['Second entity type (Chemical, Gene, Disease)'],row['Second entity name, database ID(s)'])]

				outData = [ theme, percentile, row['PubMed ID'],row['First entity type (Chemical, Gene, Disease)'],row['First entity name, database ID(s)'],name1,row['Second entity type (Chemical, Gene, Disease)'],row['Second entity name, database ID(s)'],name2,sentence ]

				outLine = "\t".join(map(str,outData))
				#assert not '\x00' in outLine, 'Null character in line %d of %s' % (lineno+1,args.partii)
				outLine = outLine.replace('\x00','')
				outF.write(outLine + "\n")

			#if lineno > 10000:
			#	continue

