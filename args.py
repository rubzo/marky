# Turn (name, value) into the appropriate argument format for execution.
def emit_argument(name, value):
	if (name[-1] == '='):
		return name + str(value)
	return name + " " + str(value)

# A recursive function for building up arguments to be used in the experiment.
def build_experiment_arguments(exp_args, arg_vars):
	if len(arg_vars) == 0:
		return exp_args
	else:
		(key, (values, is_filearg_var)) = arg_vars.popitem()
		if is_filearg_var:
			(temp_file, output_file, pattern, real_values) = values
			values = real_values

		new_exp_args = []
		if len(exp_args) == 0:
			for v in values:
				new_exp_args.append([(key, v, is_filearg_var)])
		else:
			for arg in exp_args:
				for v in values:
					new_exp_args.append(arg + [(key, v, is_filearg_var)])

		return build_experiment_arguments(new_exp_args, arg_vars)

# From a given dict of argument (name, value) pairs, generate all possible combinations of the arguments.
def get_experiment_arguments(cmdarg_vars, filearg_vars):
	exp_args = []
	# This container will contain both commandline argument variables and file argument variables.
	real_arg_vars = {}

	for (k, v) in cmdarg_vars.items():
		real_arg_vars[k] = (v, False)
	for (k, v) in filearg_vars.items():
		real_arg_vars[k] = (v, True)

	exp_args = build_experiment_arguments(exp_args, real_arg_vars)
	return exp_args
