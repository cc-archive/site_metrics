import time

import api_parse
import api_analyze

parse_start = time.time()
data = api_parse.parse()
parse_stop = time.time()

analysis_start = time.time()
api_analyze.analyze(data)
analysis_stop = time.time()

print "============================="
print "Parse time: %.2f seconds" % (parse_stop - parse_start)
print "Analysis time: %.2f seconds" % (analysis_stop - analysis_start)
