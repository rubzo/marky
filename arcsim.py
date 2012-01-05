import re

import stats

root = "/Users/sck/Code/arcsim-trunk/"

### PROGRAMS
programs = { \
"arcsim": root + "bin/arcsim", \
}

### BENCHMARK ROOT DIRECTORY
benchmark_root = root + "tests/regression/tests/"

### DEFINE BENCHMARK GROUPS HERE
eembc_default_benchmarks = [ \
("a2time01-default-iter", "eembc/default-iterations", None), \
("aifftr01-default-iter", "eembc/default-iterations", None), \
]
eembc_large_benchmarks = [ \
("a2time01-120000-iter", "eembc/large-iterations", None), \
("aifftr01-2000-iter", "eembc/large-iterations", None), \
]
bioperf_benchmarks = [ \
("clustalw", "bioperf/clustalw", "runcmd-small"), \
("grappa", "bioperf/grappa", "runcmd-small"), \
("hmmer-hmmsearch", "bioperf/hmmer-hmmsearch", "runcmd-small"), \
("tcoffee", "bioperf/tcoffee", "runcmd-small"), \
("blast-blastp", "bioperf/blast-blastp", "runcmd-small"), \
("blast-blastn", "bioperf/blast-blastn", "runcmd-small"), \
("glimmer", "bioperf/glimmer", "runcmd-small"), \
]
splash_benchmarks = [ \
("cholesky.x", "multicore/splash/cholesky", "runcmd"), \
]

# REGISTER BENCHMARK GROUPS HERE
benchmarks = { \
"eembc default": eembc_default_benchmarks, \
"eembc large": eembc_large_benchmarks, \
}

# ARGUMENTS THAT SHOULD BE VARIED
argument_variables = { \
"--fast-num-threads=": [1,100], \
}

# ARGUMENTS THAT SHOULD BE VARIED IN FILES HERE
#file_argument_variables = { \
#"cores": (root + "etc/skeleton-encore.arc", root + "etc/encore.arc", "INSERTCORESHERE", [1,2,4,8]), \
#}
file_argument_variables = {}

# ARGUMENTS THAT SHOULD ALWAYS BE THERE
core_arguments = "--fast --verbose --emt"
benchmark_argument = "-e"

# ITERATIONS
iterations = 3

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

# This is used by certain output formats.
filter_order = ["time", "mips", "interpreted instructions", "translated instructions", "total instructions"]

# REGISTER BENCHMARK (ACROSS ALL RUNS OF BENCHMARK) AGGREGATES HERE
benchmark_aggregates = { \
"arithmetric mean": (stats.arithmetric_mean, None), \
"geometric mean": (stats.geometric_mean, None), \
"maximum mips": (stats.maximum, "mips"), \
"minimum time": (stats.minimum, "time"), \
}

# REGISTER EXPERIMENT (ACROSS ALL BENCHMARKS OF EXPERIMENT) AGGREGATES HERE
# (must be a key in benchmark_aggregates)
experiment_aggregates = ["arithmetric mean"]
