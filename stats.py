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
