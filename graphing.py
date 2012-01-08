from matplotlib import pyplot as plt

# Lotta work needs to go into this...
def graph_barchart_from_dict(d):
	
	speedups = d.values()
	benchmarks = d.keys()

	ind = range(0, len(speedups))
	width = 0.15

	p1 = plt.bar(ind, speedups, width, color='blue')

	plt.ylabel('Speedup')
	plt.xticks(map(lambda n: n + width/2.0, ind), benchmarks)

	plt.show()
