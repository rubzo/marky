try:
	reduce(sum, [1])
except NameError:
	from functools import reduce

def arithmetric_mean(values):
	total = sum(values)
	return (float(total)) / len(values)

def geometric_mean(values):
	total = reduce(lambda a, b: a * b, values)
	return (float(total))**(float(1)/len(values))

def maximum(values):
	return max(values)

def minimum(values):
	return min(values)

# Run the aggregate function 'fun' over all runs in 'run_table'.
# If 'key_field' is provided, the corresponding field in the runs is
# used as the "key" of the result.
def aggregate(fun, run_table, key_field = None):
	aggregate_run = {}
	
	# *** We don't want to simply aggregate all the fields.
	# Aggregate the values in each run's key field, and use whichever run has that result in that field.
	# e.g. for getting the run with the minimum/maximum value in a given field
	if key_field:
		# Construct the list of values in the key field
		values = []
		for run in run_table:
			values.append(run[key_field])

		# Get the aggregate 
		result = fun(values)

		# Search the runs for the run with that aggregate value in its key field
		for run in run_table:
			if run[key_field] == result:
				# Found it, store it in our object to be returned.
				aggregate_run = run

		# The resulting aggregate run MUST be set to something!
		# If not, the aggregate value obviously wasn't part of any of the runs!
		assert len(aggregate_run) > 0

	# We DO simply want to aggregate all the fields.
	else:
		# Use the first run in the run table as example of the run's schema (i.e., fields)
		for field in run_table[0].keys():
			# For each field...
			# ...construct the list of values in that field
			values = []
			for run in run_table:
				values.append(run[field])

			# Add the aggregate of those values to the aggregate run
			aggregate_run[field] = fun(values)	

	return aggregate_run

# This is called by run() every time it finishes running a given experiment.
def perform_experiment_aggregation(suite, experiment_table):
	experiment_table["aggregates"] = {}
		
	# experiment_aggregates contains a list of names of benchmark aggregates
	# We wish to take the aggregate run with this name from each benchmark in the experiment
	# and combine those into one aggregate run!
	for aggregate_name in suite.experiment_aggregates:
		# Where we store each benchmark's aggregate runs as a run...
		run_table = []

		# Get the right aggregate function and key field with this name
		(aggregate_fun, key_field) = suite.benchmark_aggregates[aggregate_name]

		# Go through the benchmarks executed in this experiment... 
		for (name, benchmark) in experiment_table["benchmarks"].items():
			# Populating the run_table
			run_table.append(benchmark["aggregates"][aggregate_name])

		# Now present the run table to aggregate.aggregate, which simply treats it as it would if it were 
		# aggregating a list of runs for a single benchmark!
		experiment_table["aggregates"][aggregate_name] = aggregate(aggregate_fun, run_table, key_field)


def perform_aggregation(suite, results):
	for (exp_name, exp) in results["experiments"].items():
		successes = 0
		for (bm_name, bm) in exp["benchmarks"].items():
			if bm["successes"] > 0 and len(suite.benchmark_aggregates) > 0:
				successes += 1
				bm["aggregates"] = {}
				for (field, (a, key_field)) in suite.benchmark_aggregates.items():
					bm["aggregates"][field] = aggregate(a, bm["runs"], key_field)

		if successes > 0 and len(suite.experiment_aggregates) > 0:
			exp["aggregates"] = {}
			perform_experiment_aggregation(suite, exp)


def calculate_speedups(results):
	assert len(results["experiments"]) == 2
	results["speedups"] = {}
	exps = results["experiments"].keys()
	calculate_benchmark_speedups(results, exps[0], exps[1])
	calculate_benchmark_speedups(results, exps[1], exps[0])

# TODO: This is not generic yet!
def calculate_benchmark_speedups(results, before_name, after_name):
	# Make sure the speedups field is present.
	if "speedups" not in results.keys():
		results["speedups"] = {}

	speedup_table = {}
	before = results["experiments"][before_name]
	after = results["experiments"][after_name]
	benchmarks = before["benchmarks"].keys()
	for bm_name in benchmarks:
		average_runtime = before["benchmarks"][bm_name]["aggregates"]["arithmetric mean"]["time"]
		speedups = []
		for run in after["benchmarks"][bm_name]["runs"]:
			runtime = run["time"]
			speedup = float(average_runtime) / runtime
			speedups.append(speedup)
		speedup_table[bm_name] = arithmetric_mean(speedups)
	results["speedups"][before_name + " -> " + after_name] = speedup_table
