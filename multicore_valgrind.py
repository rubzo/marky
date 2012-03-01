import arcsimMemAnalyzer
import re
import time

import stats

root = "/disk/scratch/vseeker/workspace/arcsim/rep/arcsim_multicore/"

### PROGRAMS
programs = { \
"arcsim": root + "src/arcsim", \
}

### BENCHMARK ROOT DIRECTORY
#benchmark_root = root + "tests/regression/tests/"
benchmark_root = "/disk/scratch/vseeker/workspace/arcsim/rep/arcsim_trunk/trunk/tests/regression/tests/"

### DEFINE BENCHMARK GROUPS HERE
splash_benchmarks = [ \
("a2time01-default-iter", "eembc/default-iterations", None, 160), \
#("barnes.x", "multicore/splash/barnes", "runcmd", 6800), \
#("cholesky.x", "multicore/splash/cholesky", "runcmd", 400), \
#("fft.x", "multicore/splash/fft", "runcmd", 2000), \
#("fmm.x", "multicore/splash/fmm", "runcmd", 600), \
#("lu.x", "multicore/splash/lu", "runcmd", 400), \
#("ocean.x", "multicore/splash/ocean", "runcmd", 2000), \
#("radiosity.x", "multicore/splash/radiosity", "runcmd", 1000), \
#("radix.x", "multicore/splash/radix", "runcmd", 300), \
#("raytrace.x", "multicore/splash/raytrace", "runcmd", 400), \
#("volrend.x", "multicore/splash/volrend", "runcmd", 1500), \
#("water-nsquared.x", "multicore/splash/water-nsquared", "runcmd", 600), \
#("water-spatial.x", "multicore/splash/water-spatial", "runcmd", 600), \
]

# REGISTER BENCHMARK GROUPS HERE
benchmarks = { \
"splash": splash_benchmarks, \
}

# ARGUMENTS THAT SHOULD BE VARIED
argument_variables = {}

# ARGUMENTS THAT SHOULD BE VARIED IN FILES HERE
file_argument_variables = { \
"cores": (root + "etc/skeleton-encore.arc", root + "etc/encore.arc", "INSERTCORESHERE", [1]), \
}

massif_out_file = "massifOutFile"

# ARGUMENTS THAT SHOULD ALWAYS BE THERE
pre_arguments = "valgrind --tool=massif --time-unit=ms --massif-out-file=" + massif_out_file
core_arguments = "--fast --verbose"
benchmark_argument = "-e"

# ITERATIONS
iterations = 1

# DEFINE FILTERS HERE
time_filter = re.compile("\[SYSTEM\] Total Simulation time[ ]*= ([^ ]+) \[Seconds\]")
mips_filter = re.compile("\[SYSTEM\] Overall Simulation rate[ ]*= ([^ ]+) \[MIPS\]")
interp_inst_filter = re.compile("\[SYSTEM\] Total Interpreted instructions[ ]*= (\d+) \[Instructions\]")
trans_inst_filter = re.compile("\[SYSTEM\] Total Translated instructions[ ]*= (\d+) \[Instructions\]")
total_inst_filter = re.compile("\[SYSTEM\] Total Instructions[ ]*= (\d+)")

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

# Postfunctions
post_function = arcsimMemAnalyzer.analyzeArcSimMem

def get_start_time():
    return time.time() * 1000 # in ms

# Postfunction arguments
post_function_arguments = [ "arcsimMemOutPut.csv", \
                       massif_out_file, \
                       "GETUNIQUEFILENAME", \
                       "GETTIMESTAMP" \
                     ]