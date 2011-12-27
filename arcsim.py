import re

import aggregate

programs = str.split("""
/Users/sck/Code/arcsim-trunk/bin/arcsim
""")

benchmarks = str.split("""
a2time01-default-iter
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
