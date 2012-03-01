import matplotlib
matplotlib.use("AGG")

from matplotlib import pyplot as plt
import matplotlib.transforms as transforms

class Graph:
	def __init__(self, fig, ax, num):
		self.colors = ["black", "grey", "blue", "red", "green"]
		self.color_idx = 0
		self.fig = fig
		self.ax = ax
		self.offset_points = 0
		self.next_color = self.colors[self.color_idx]
		self.high_yaxis = 2.0
		self.benchmarks_num = num
		self.plots = []
		self.num_plots = 0

	def change_color(self):
		self.color_idx += 1
		if (self.color_idx == len(self.colors)):
			self.color_idx = 0
		self.next_color = self.colors[self.color_idx]

def setup_graph(title, benchmarks_num, xlabel, ylabel, plot_names):
	fig = plt.figure()
	ax = fig.add_subplot(111)

	graph = Graph(fig, ax, benchmarks_num)

	ax.set_title(title, fontsize=10)
	ax.set_xlabel(xlabel, fontsize=10)
	ax.set_ylabel(ylabel, fontsize=10)
	ax.axis([-1, graph.benchmarks_num, 0, graph.high_yaxis])

	if (ylabel == "Speedup"):
		ax.axhline(1.0, color="black", linewidth=0.5)

	graph.plot_names = plot_names

	graph.num_plots = len(plot_names)

	return graph

def add_plot(graph, names, values, errors):
	fig = graph.fig
	ax = graph.ax
	offset_points = graph.offset_points
	color = graph.next_color

	offset = transforms.ScaledTranslation(offset_points/72.0, 0, fig.dpi_scale_trans)
	offset_transform = ax.transData + offset

	(plot, bar1, bar2) = ax.errorbar(xrange(0,len(values)), values, yerr=errors, marker="D", markersize=2.5, linestyle=" ", color=color, transform=offset_transform, markeredgecolor=color, elinewidth=0.8)

	graph.plots.append(plot)

	graph.change_color()

	for i in xrange(0, len(values)):
		high_point = values[i] + errors[i]
		if high_point > graph.high_yaxis:
			graph.high_yaxis = high_point
			graph.high_yaxis = graph.high_yaxis * 1.05
			ax.axis([-1, graph.benchmarks_num, 0, graph.high_yaxis])

	width = 0.15

	ind = range(0, len(values))
	plt.xticks(map(lambda n: n + width/2.0, ind), names, fontsize=8, rotation=300)
	plt.yticks(fontsize=8)

	graph.offset_points += 4

def output_graph(graph, graph_name):
	graph.ax.legend(graph.plots, graph.plot_names, prop={'size': 8, 'family': 'Arial'})

	graph.fig.savefig(graph_name)
	
