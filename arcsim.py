import re
import aggregate

### PROGRAMS
programs = { \
"arcsim": "/Users/sck/Code/arcsim-trunk/bin/arcsim", \
}

### BENCHMARK ROOT DIRECTORY
benchmark_root = "/Users/sck/Code/arcsim-trunk/tests/regression/tests"

### DEFINE BENCHMARK GROUPS HERE
eembc_default_benchmarks = [ \
("a2time01-default-iter", "eembc/default-iterations", None), \
("aifftr01-default-iter", "eembc/default-iterations", None), \
]
eembc_large_benchmarks = [ \
("a2time01-120000-iter", "eembc/large-iterations", None), \
("aifftr01-2000-iter", "eembc/large-iterations", None), \
]

# REGISTER BENCHMARK GROUPS HERE
benchmarks = { \
"eembc default": eembc_default_benchmarks, \
"eembc large": eembc_large_benchmarks, \
}

# ARGUMENTS THAT SHOULD BE VARIED
argument_variables = { \
"--fast-num-threads=": [10,100], \
}

# ARGUMENTS THAT SHOULD ALWAYS BE THERE
core_arguments = "--fast --verbose"
benchmark_argument = "-e"

# ITERATIONS
iterations = 2

# DEFINE FILTERS HERE
time_filter = re.compile("Simulation time = ([^ ]+) \[Seconds\]")
mips_filter = re.compile("Simulation rate = ([^ ]+) \[MIPS\]")
interp_inst_filter = re.compile("Interpreted instructions[ ]*= (\d+)")
trans_inst_filter = re.compile("Translated instructions[ ]*= (\d+)")
total_inst_filter = re.compile("Total instructions[ ]*= (\d+)")

# REGISTER FILTERS HERE
filters = { \
"time": time_filter, \
"mips": mips_filter, \
"interpreted instructions": interp_inst_filter, \
"translated instructions": trans_inst_filter, \
"total instructions": total_inst_filter, \
}

# REGISTER BENCHMARK (ACROSS ALL RUNS OF BENCHMARK) AGGREGATES HERE
benchmark_aggregates = { \
"arithmetric mean": (aggregate.arithmetric_mean, None), \
"geometric mean": (aggregate.geometric_mean, None), \
"maximum mips": (aggregate.maximum, "mips"), \
"minimum time": (aggregate.minimum, "time"), \
}

# REGISTER EXPERIMENT (ACROSS ALL BENCHMARKS OF RUN) AGGREGATES HERE
# (must be a key in benchmark_aggregates)
experiment_aggregates = ["arithmetric mean"]
