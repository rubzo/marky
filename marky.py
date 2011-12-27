#!/usr/bin/env python

import os, subprocess, re, sys, pprint, json

import aggregate

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
		n = float(s)
	except ValueError:
		try:
			n = int(s)
		except ValueError:
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

# Functions that should be exposed to main are below:

# This function is actually used to execute the experiments.
# It returns a currently-amorphous table of information about the experiments.
def run(suite):
	total_result_table = {}
	for program in suite.programs:

		if (len(suite.argument_variables) == 0):
			total_result_table[(program, None)] = run_experiment(program)
		else:
			for experiment_arguments in get_experiment_arguments(suite.argument_variables):
				total_result_table[program + " " + experiment_arguments] = run_experiment(program, experiment_arguments)

	return total_result_table

def run_experiment(program, experiment_arguments = ""): 

	experiment_table = {}

	for benchmark in suite.benchmarks:

		run_table = []
		failed_iterations = 0

		for i in range(suite.iterations):

			run = {}

			invocation = " ".join([program, suite.core_arguments, experiment_arguments, suite.benchmark_argument, benchmark])

			print "RUN: '" + invocation + "' (ITER: " + str(i+1) + "/" + str(suite.iterations) + ")"

			raw = ""
			try:
				raw = execute_and_capture_output(invocation)
				for (field, field_filter) in suite.filters.items():
					run[field] = run_filter(raw, field_filter)

				run = cleanup_run(run)

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
			for (field, (a, key_field)) in suite.aggregates.items():
				benchmark_result["aggregates"][field] = aggregate.aggregate(a, run_table, key_field)

		experiment_table[benchmark] = benchmark_result
	
	return experiment_table

# Used by the main function below, change which function implements the service here.
# Prints the results!
def print_results(results):
	simple_print(results)

# Used by the main function below, change which function implements the service here.
# Saves the results!
def save_results(filename, results):
	dump_json(filename, results)

# Prints usage!
def print_usage():
	print "usage: marky.py --file <description file> [--save <file>] [--print]"

# Prints help!
def print_help():
	print "marky - a benchmark execution and statistics gathering framework"
	print_usage()
	print
	print " --file <description file> - a file containing an execution configuration"
	print " --save <file>             - output the results into a JSON file"
	print " --print                   - \"pretty-print\" the results"
	
#
# MAIN FUNCTION
#
if __name__ == "__main__":

	if ('-h' in sys.argv or '--help' in sys.argv):
		print_help()
		exit(0)

	success = True
	suite = 0
	if "--file" in sys.argv:
		idx = sys.argv.index("--file")+1
		if idx < len(sys.argv):
			suite = __import__(sys.argv[idx])
		else:
			success = False
	else:
		success = False

	if (not success):
		print "Unable to load an execution configuration file!"
		print_usage()
		exit(1)

	results = run(suite)
	if "--print" in sys.argv:
		print_results(results)
	if "--save" in sys.argv:
		idx = sys.argv.index("--save")+1
		if idx < len(sys.argv):
			save_results(sys.argv[idx], results)
		else:
			print "Missing a filename to save JSON to!"
			print_usage()
			exit(1)
