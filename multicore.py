import re

import stats

root = "/disk/data5/s0562338/trunk_multicore/"

### PROGRAMS
programs = { \
"arcsim-private": root + "bin/arcsim-private", \
"arcsim-share": root + "bin/arcsim-share", \
}

### BENCHMARK ROOT DIRECTORY
benchmark_root = root + "tests/regression/tests/"

### DEFINE BENCHMARK GROUPS HERE
splash_benchmarks = [ \
("barnes.x", "multicore/splash/barnes", "runcmd", None), \
("cholesky.x", "multicore/splash/cholesky", "runcmd", None), \
("fft.x", "multicore/splash/fft", "runcmd", None), \
("fmm.x", "multicore/splash/fmm", "runcmd", None), \
("lu.x", "multicore/splash/lu", "runcmd", None), \
("ocean.x", "multicore/splash/ocean", "runcmd", None), \
("radiosity.x", "multicore/splash/radiosity", "runcmd", None), \
("radix.x", "multicore/splash/radix", "runcmd", None), \
("raytrace.x", "multicore/splash/raytrace", "runcmd", None), \
("volrend.x", "multicore/splash/volrend", "runcmd", None), \
("water-nsquared.x", "multicore/splash/water-nsquared", "runcmd", None), \
("water-spatial.x", "multicore/splash/water-spatial", "runcmd", None), \
]

# REGISTER BENCHMARK GROUPS HERE
benchmarks = { \
"splash": splash_benchmarks, \
}

# ARGUMENTS THAT SHOULD BE VARIED
argument_variables = {}

# ARGUMENTS THAT SHOULD BE VARIED IN FILES HERE
file_argument_variables = { \
"cores": (root + "etc/skeleton-encore.arc", root + "etc/encore.arc", "INSERTCORESHERE", [4,32,128]), \
}

# ARGUMENTS THAT SHOULD ALWAYS BE THERE
core_arguments = "--fast --fast-num-threads=3 --verbose"
benchmark_argument = "-e"

# ITERATIONS
iterations = 1

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
