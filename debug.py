from config import config

warnings = 0

def debug_msg(level, msg):
	if config["debuglevel"] >= level:
		spacer = "  " * (level-1)
		print spacer + "[D" + str(level) + "] " + msg

def warning_msg(msg):
	if config["debuglevel"] > 0:
		print "[WARNING] " + msg
		warnings += 1

def error_msg(msg):
	print "[ERROR] " + msg
	print "Quitting..."
	exit(1)

def seen_warnings():
	return (warnings > 0)

def reset_warnings():
	warnings = 0
