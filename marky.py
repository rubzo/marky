import os
import subprocess
import re
import pprint
import sys
import json

# Function used to capture all output from a program it executes.
# Executes the whole program before returning any output.
def unsafe_execute_and_capture_output(program):
	p = subprocess.Popen(program, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
	output = ""
	line = p.stdout.readline()
	while line:
		output += line
		line = p.stdout.readline()
	return output

# Function used to capture all output from a program it executes.
# Executes the whole program before returning any output.
def safe_execute_and_capture_output(program):
	output = 0
	try:
		output = subprocess.check_output(program, shell=True, stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		# TODO: Work out how on earth I get information about the error!
		raise e
	return output

execute_and_capture_output = safe_execute_and_capture_output

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
def cleanup_run(r):
	for key in r.keys():
		r[key] = convert_data(r[key])
	return r

def emit_argument(key, value):
	if (key[-1] == '='):
		return key + str(value)
	return key + " " + str(value)

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

def get_experiment_arguments(arg_vars):
	exp_args = []
	arg_vars_copy = dict(arg_vars)
	exp_args = build_experiment_arguments(exp_args, arg_vars_copy)
	return exp_args

# Just uses a simple pretty printer.
def simple_print(results):
	pprint.pprint(results)

def dump_json(filename, results):
	f = open(filename, "w")
	json.dump(results, f)
	f.close()
