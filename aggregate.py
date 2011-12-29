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

# Run the aggregate function 'fun' over all rGuns in 'run_table'.
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
