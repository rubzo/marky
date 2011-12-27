import re

import marky
import aggregate

benchmarks = str.split("""
a2time01-default-iter
""")

programs = str.split("""
/Users/sck/Code/arcsim-trunk/bin/arcsim
""")

argument_variables = { \
"--fast-num-threads=": range(1,4), \
}

core_arguments = "--fast --verbose"
benchmark_argument = "-e"

iterations = 3

time_filter = re.compile("Simulation time = ([^ ]+) \[Seconds\]")
mips_filter = re.compile("Simulation rate = ([^ ]+) \[MIPS\]")
interp_inst_filter = re.compile("Interpreted instructions[ ]*= (\d+)")
trans_inst_filter = re.compile("Translated instructions[ ]*= (\d+)")
total_inst_filter = re.compile("Total instructions[ ]*= (\d+)")

filters = { \
"time": time_filter, \
"mips": mips_filter, \
"interpreted instructions": interp_inst_filter, \
"translated instructions": trans_inst_filter, \
"total instructions": total_inst_filter, \
}

aggregates = { \
"arithmetric mean": (aggregate.arithmetric_mean, None), \
"geometric mean": (aggregate.geometric_mean, None), \
"maximum mips": (aggregate.maximum, "mips"), \
"minimum time": (aggregate.minimum, "time"), \
}

def run():
	total_result_table = {}
	for program in programs:

		if (len(argument_variables) == 0):
			total_result_table[(program, None)] = run_experiment(program)
		else:
			for experiment_arguments in marky.get_experiment_arguments(argument_variables):
				total_result_table[program + " " + experiment_arguments] = run_experiment(program, experiment_arguments)

	return total_result_table

def run_experiment(program, experiment_arguments = ""): 

	experiment_table = {}

	for benchmark in benchmarks:

		run_table = []
		failed_iterations = 0

		for i in range(iterations):

			run = {}

			invocation = " ".join([program, core_arguments, experiment_arguments, benchmark_argument, benchmark])

			print "RUN: '" + invocation + "' (ITER: " + str(i+1) + "/" + str(iterations) + ")"

			raw = ""
			try:
				raw = marky.execute_and_capture_output(invocation)
				for (field, field_filter) in filters.items():
					run[field] = marky.run_filter(raw, field_filter)

				run = marky.cleanup_run(run)

				run_table.append(run)
			except Exception:
				failed_iterations += 1

		benchmark_result = {}
		benchmark_result["successes"] = len(run_table)
		benchmark_result["failures"] = failed_iterations
		benchmark_result["attempts"] = len(run_table) + failed_iterations

		if len(run_table) > 0:
			benchmark_result["runs"] = run_table
			benchmark_result["aggregates"] = {}
			for (field, (a, key_field)) in aggregates.items():
				benchmark_result["aggregates"][field] = aggregate.aggregate(a, run_table, key_field)

		experiment_table[benchmark] = benchmark_result
	
	return experiment_table

def print_results(results):
	marky.simple_print(results)

def save_results(filename, results):
	marky.dump_json(filename, results)

