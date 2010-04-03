import time

import logparse
import api_analyze

def run_all():
    parse_start = time.time()
    data = logparse.parse()
    parse_stop = time.time()

    analysis_start = time.time()
    api_analyze.analyze(data)
    analysis_stop = time.time()

    print "============================="
    print "Parse time: %.2f seconds" % (parse_stop - parse_start)
    print "Analysis time: %.2f seconds" % (analysis_stop - analysis_start)

def run_test(): # not really sure what was going on here...
    data = logparse.parse()#api_parse.minimal_parse()
    f = open('paths.txt','w')
    for d in data:
        f.write("%s %s\n" % (d[0], d[1]))

if __name__ == '__main__':
    run_all()
