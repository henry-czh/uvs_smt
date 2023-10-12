import sys
import traceback

def log(log_str):
    if not isinstance(log_str, str):
        log_str = "%s" % log_str
    trace = traceback.extract_stack()[-2]
    f = trace[0].split('/')[-1]
    sys.stderr.write("%s:%d(%s) %s\n" % (f, trace[1], trace[2], log_str))

