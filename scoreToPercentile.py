

def scoresToPercentiles(scores):
	converter = {}
	prev = None
	running = []

	sorted_scores = sorted(scores)
	sorted_scores.append(None)

	for i,s in enumerate(sorted_scores):
		print(i,s,running)
		if s == prev:
			running.append(i)
		else:
			if running:
				converter[prev] = sum(running) / len(running)
				running = []
			prev = s

	return converter


scores = [2,5,3,2,1]

print(scoresToPercentiles(scores))
