import json
import numpy
import math
import re

import graphing
import tinv
from debug import warning_msg, debug_msg

confidence_alpha = 0.95

def gather_data_points(runs, column_name):
	data = []
	for run in runs:
		data.append(run[column_name])
	return data

def calculate_CI(values):
	count = len(values)
	average = numpy.mean(values)
	variance = numpy.var(values)
	std_err = math.sqrt(float(variance) / float(count))
	degs_freedom = count - 1
	t_value = tinv.tinv(1 - confidence_alpha, degs_freedom)

	margin_error = std_err * t_value
	#margin_error = std_err #???

	return (average - margin_error, average, average + margin_error)
	
def calculate_mean(results, exp_name, column_name):
	mean_table = {}
	exp = results["experiments"][exp_name]
	benchmarks = exp["benchmarks"].keys()

	for bm_name in benchmarks:
		if "runs" not in exp["benchmarks"][bm_name]:
			warning_msg(exp_name)
			warning_msg(bm_name)
			warning_msg("No successful runs occurred for experiment.")
			mean_table[bm_name] = (0, 0, 0)
			continue
		data = gather_data_points(exp["benchmarks"][bm_name]["runs"], column_name)
		(lower, mean, upper) = calculate_CI(data)
		mean_table[bm_name] = (lower, mean, upper)
	
	return mean_table

def calculate_speedup(results, exp_a_name, exp_b_name, column_name):
	speedup_table = {}
	exp_a = results["experiments"][exp_a_name]
	exp_b = results["experiments"][exp_b_name]
	benchmarks = exp_a["benchmarks"].keys()

	for bm_name in benchmarks:
		if "runs" not in exp_a["benchmarks"][bm_name]:
			warning_msg(exp_a_name)
			warning_msg(bm_name)
			warning_msg("No successful runs occurred for experiment.")
			speedup_table[bm_name] = (1.0, 1.0, 1.0)
			continue
		if "runs" not in exp_b["benchmarks"][bm_name]: 
			warning_msg(exp_b_name)
			warning_msg(bm_name)
			warning_msg("No successful runs occurred for experiment.")
			speedup_table[bm_name] = (1.0, 1.0, 1.0)
			continue
		data_a = gather_data_points(exp_a["benchmarks"][bm_name]["runs"], column_name)
		data_b = gather_data_points(exp_b["benchmarks"][bm_name]["runs"], column_name)
		average = numpy.mean(data_a)  
		speedups = []
		for v in data_b: 
			speedup = float(average) / v
			speedups.append(speedup)
		(lower, mean, upper) = calculate_CI(speedups)
		speedup_table[bm_name] = (lower, mean, upper)

	return speedup_table

def get_mean_with_CI(results, exp_name, column_name):
	speedup_table = calculate_mean(results, exp_name, column_name)

	lowers = []
	means = []
	uppers = []

	names = speedup_table.keys()
	names.sort()

	for name in names:
		(l, m, u) = speedup_table[name]
		lowers.append(l)
		means.append(m)
		uppers.append(u)

	group_remover = re.compile(".* \+\+ (.*)\.x")
	names = map(lambda name: group_remover.match(name).group(1), names)

	errors = []
	for i in xrange(0, len(means)):
		errors.append(means[i] - lowers[i])

	return (names, means, errors)

def get_speedup_with_CI(results, exp_a_name, exp_b_name, column_name):
	speedup_table = calculate_speedup(results, exp_a_name, exp_b_name, column_name)

	lowers = []
	means = []
	uppers = []

	names = speedup_table.keys()
	names.sort()

	for name in names:
		(l, m, u) = speedup_table[name]
		lowers.append(l)
		means.append(m)
		uppers.append(u)

	group_remover = re.compile(".* \+\+ (.*)\.x")
	names = map(lambda name: group_remover.match(name).group(1), names)

	errors = []
	for i in xrange(0, len(means)):
		errors.append(means[i] - lowers[i])

	return (names, means, errors)

def calculate(results):
	#for i in [2,4,8,16,32]:
	#	_calculate(results, i)
	_calculate(results, 1)

def _calculate(results, cores):
	cores = str(cores)

	graph = graphing.setup_graph("Runtime using 32 cores with Varying Workers", 12, "Benchmark", "Time (s)", ["1 worker", "2 workers", "3 workers", "16 workers", "32 workers"])
	
	for workers in [1,2,3,16,32]:
		exp_name = "arcsim-share cores:32 --fast-num-threads=" + str(workers) 

		(names, means, errors) = get_mean_with_CI(results, exp_name, "time")
		graphing.add_plot(graph, names, means, errors)

	graphing.output_graph(graph, "graph-varying-workers-share.png")

#	graph = graphing.setup_graph("Speedup, with " + cores + " Cores", 12, "Benchmark", "Speedup", ["share", "global-page"])
#	
#	exp_a_name = "arcsim-private cores:" + cores + " "
#	exp_b_name = "arcsim-share cores:" + cores + " "
#	exp_c_name = "arcsim-global-page cores:" + cores + " "
#
#	(names, means, errors) = get_speedup_with_CI(results, exp_a_name, exp_b_name, "time")
#	graphing.add_plot(graph, names, means, errors)
#	(names, means, errors) = get_speedup_with_CI(results, exp_a_name, exp_c_name, "time")
#	graphing.add_plot(graph, names, means, errors)
#
#	graphing.output_graph(graph, "graph-runtime-" + cores + ".png")
#
#	graph = graphing.setup_graph("JIT Compilation Time, with " + cores + " Cores", 12, "Benchmark", "Time (s)", ["private", "share", "global-page"])
#	
#	(names, means, errors) = get_mean_with_CI(results, exp_a_name, "average jit time")
#	graphing.add_plot(graph, names, means, errors)
#	(names, means, errors) = get_mean_with_CI(results, exp_b_name, "average jit time")
#	graphing.add_plot(graph, names, means, errors)
#	(names, means, errors) = get_mean_with_CI(results, exp_c_name, "average jit time")
#	graphing.add_plot(graph, names, means, errors)
#
#	graphing.output_graph(graph, "graph-jittime-" + cores + ".png")
#
#	graph = graphing.setup_graph("Registered Translations, with " + cores + " Cores", 12, "Benchmark", "# Registered Translations", ["private", "share", "global-page"])
#	
#	(names, means, errors) = get_mean_with_CI(results, exp_a_name, "registered translations")
#	graphing.add_plot(graph, names, means, errors)
#	(names, means, errors) = get_mean_with_CI(results, exp_b_name, "registered translations")
#	graphing.add_plot(graph, names, means, errors)
#	(names, means, errors) = get_mean_with_CI(results, exp_c_name, "registered translations")
#	graphing.add_plot(graph, names, means, errors)
#
#	graphing.output_graph(graph, "graph-regtrans-" + cores + ".png")



