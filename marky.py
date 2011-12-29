#!/usr/bin/env python

import os, subprocess, re, sys, string, pprint, json, argparse

import aggregate, mailer

# Function used to capture all output from a program it executes.
# Executes the whole program before returning any output.
def execute_and_capture_output(program):
	output = 0
	try:
		output = subprocess.check_output(program, shell=True, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		# TODO: Work out how on earth I get information about the error!
		raise e
	return output

# Implementation of pushd
directories = []
def enter_directory(directory):
	global directories
	directories.append(os.getcwd())
	try:
		os.chdir(directory)
	except Error:
		directories.pop()

# Implementation of popd
def leave_directory():
	global directories
	os.chdir(directories.pop())

# This program will run a filter (regular expression) on benchmark output,
# and will return the first value that was captured within parens.
def run_filter(raw, filter_function):
	match = re.search(filter_function, raw)
	if match:
		return match.group(1)
	else:
		return None

# Should do similar to the above, but return a list of all matches
# that were between parens.
def run_multi_filter(raw, filter_function):
	pass

# Attempt to convert a string of data to the correct type.
def convert_data(s):
	n = s
	try:
		n = int(s)
		# s must've been an int!
	except ValueError:
		try:
			n = float(s)
			# s must've been a float!
		except ValueError:
			# s isn't a float or an int, assume it's a string.
			n = s
	return n

# For a run, converts all the data in it to the correct type.
def cleanup_run(run):
	for field in run.keys():
		run[field] = convert_data(run[field])
	return run

# Turn (key, value) into the appropriate argument format for execution.
def emit_argument(key, value):
	if (key[-1] == '='):
		return key + str(value)
	return key + " " + str(value)

# A recursive function for building up arguments to be used in the experiment.
def build_experiment_arguments(exp_args, arg_vars):
	if len(arg_vars) == 0:
		return exp_args
	else:
		(key, values) = arg_vars.popitem()
		new_exp_args = []
		if len(exp_args) == 0:
			for v in values:
				new_exp_args.append(emit_argument(key, v))
		else:
			for arg in exp_args:
				for v in values:
					new_exp_args.append(arg + " " + emit_argument(key, v))
		return build_experiment_arguments(new_exp_args, arg_vars)

# From a given dict of argument (key, value) pairs, generate all possible combinations.
def get_experiment_arguments(arg_vars):
	exp_args = []
	arg_vars_copy = dict(arg_vars)
	exp_args = build_experiment_arguments(exp_args, arg_vars_copy)
	return exp_args

# Just use the simple pprint pretty printer.
def simple_print(results):
	pprint.pprint(results)

# Store data to disk with JSON.
def dump_json(filename, results):
	f = open(filename, "w")
	json.dump(results, f)
	f.close()
	print "SAVE: Saved JSON to " + filename + "."

def perform_experiment_aggregation(suite, experiment_table):
	experiment_table["aggregates"] = {}
		
	# program_aggregates contains a list of names of benchmark aggregates
	# We wish to take the aggregate run with this name from each benchmark in the experiment
	# and combine those into one aggregate run!
	for aggregate_name in suite.program_aggregates:
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
		experiment_table["aggregates"][aggregate_name] = aggregate.aggregate(aggregate_fun, run_table, key_field)

# -----
# Functions that should be exposed to main are below:
# -----

# This function is actually used to execute the experiments.
# It returns a currently-amorphous table of information about the experiments.
def run(suite):
	# The amorphous monstrosity of a table
	total_result_table = {}

	# Go through the programs...
	for program in suite.programs:

		# Check if there's argument variables that will require iterating over
		if (len(suite.argument_variables) == 0):
			# There were none, so simply run this program with no extra arguments
			total_result_table[program] = run_experiment(suite, program)
			# Perform aggregation
			perform_experiment_aggregation(suite, total_result_table[program])
		else:
			# There are some, so use get_experiment_arguments to get a list of all combinations, iterate over them.	
			for experiment_arguments in get_experiment_arguments(suite.argument_variables):
				total_result_table[program + " " + experiment_arguments] = run_experiment(suite, program, experiment_arguments)
				# Perform aggregation
				perform_experiment_aggregation(suite, total_result_table[program + " " + experiment_arguments])


	return total_result_table

# An "experiment" is categorised as any program + the arguments we wish to use for that program.
def run_experiment(suite, program, experiment_arguments = ""): 

	experiment_table = {}
	experiment_table["benchmarks"] = {}

	# Go through the benchmarks...
	for benchmark in suite.benchmarks:

		# We store all the runs in here.
		run_table = []
		failed_iterations = 0

		# Go through the iterations...
		for i in range(suite.iterations):

			# This stores the fields collected for this run.
			run = {}

			# Construct the command used to execute the benchmark
			invocation = " ".join([program, suite.core_arguments, experiment_arguments, suite.benchmark_argument, benchmark])

			print "RUN: '" + invocation + "' (ITER: " + str(i+1) + "/" + str(suite.iterations) + ")"

			# string containing the raw output from the benchmark
			raw = ""
			try:
				# Actually execute the benchmark
				raw = execute_and_capture_output(invocation)
				# Now collect the fields using our provided filters.
				for (field, field_filter) in suite.filters.items():
					run[field] = run_filter(raw, field_filter)

				# Collected data is all strings currently; convert to the correct types.
				run = cleanup_run(run)

				# Save this run
				run_table.append(run)

			except Exception:
				# Something bad happened when running the benchmark, just ignore it and keep going.	
				failed_iterations += 1

		# Finished running this benchmark for X iterations...
		benchmark_result = {}
		benchmark_result["successes"] = len(run_table)
		benchmark_result["failures"] = failed_iterations
		benchmark_result["attempts"] = len(run_table) + failed_iterations

		# Perform aggregation
		if len(run_table) > 0:
			benchmark_result["runs"] = run_table
			benchmark_result["aggregates"] = {}
			for (field, (a, key_field)) in suite.benchmark_aggregates.items():
				benchmark_result["aggregates"][field] = aggregate.aggregate(a, run_table, key_field)

		# Save this benchmark in the benchmark table
		experiment_table["benchmarks"][benchmark] = benchmark_result
	
	return experiment_table

# Used by the main function below, change which function implements the service here.
# Prints the results!
print_results = simple_print
# Saves the results!
save_results = dump_json
# Email the results!
email_results = mailer.send_email

#
# MAIN FUNCTION
#
def main():
	parser = argparse.ArgumentParser(
			description = "marky - a benchmark execution and statistics gathering framework")
	parser.add_argument('file', type=str, nargs=1, metavar='FILE', 
			help='A file containing an execution configuration. (Minus the .py)')
	parser.add_argument('--save', '-s', dest='should_save', nargs=1, metavar='FILE', 
			help='Output the results into a JSON file.')
	parser.add_argument('--print', '-p', dest='should_print', action='store_true', 
			help='"Pretty-print" the results.')
	parser.add_argument('--email', '-m', dest='should_email', nargs=1, metavar='ADDRESS', 
			help='Send an email to the address once complete. (Uses localhost unless --mailserver is given.)')
	parser.add_argument('--email-format', '-mf', dest='emailfmt', nargs=1, choices=["pprint","json"], 
			help='Choose between pprint and json for the format of the data sent in the email.')
	parser.add_argument('--mailserver', '-ms', dest='mailserver', nargs=1, metavar='HOST', 
			help='Use the provided host as a mailserver.')
	args = parser.parse_args()

	suite = 0
	if args.file:
		# (ecd = Execution Configuration Description)
		ecd = args.file[0]
		ecd = string.replace(ecd, ".py", "")
		suite = __import__(ecd)

	results = run(suite)

	# Print-related
	if args.should_print:
		print_results(results)

	# Saving-related
	if args.should_save:
		save_results(args.should_save[0], results)

	# Email-related
	if args.should_email:
		mailserver = 'localhost'
		if args.mailserver:
			mailserver = args.mailserver[0]
		formatter = pprint.pprint
		if args.emailfmt[0] == 'json':
			formatter = json.dumps

		email_results(args.should_email[0], results, mailserver=mailserver, formatter=formatter)

if __name__ == "__main__":
	main()
