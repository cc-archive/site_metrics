import glob
from datetime import datetime
import time
import urlparse

def parse_query(qstr):
    if qstr == '':
        return None
    else:
        pairs = qstr.split('&')
        while '' in pairs:
            pairs.remove('')
        # hack
        for i in range(len(pairs)):
            if not '=' in pairs[i]:
                pairs[i] += '='
        return dict([x.split('=') for x in pairs])

def parse_path(pstr):
    pieces = pstr.split('/')
    assert pieces[0] == ''
    if pieces[1] != 'rest':
        return None
    # hack
    if len(pieces) < 3:
        return dict(version='None', call=['None'])
    return dict(version=pieces[2], call=pieces[3:])

def parse_line(line):
    datum = {}
    line = line[len("127.0.0.1 - - "):] # chop off beginning
    assert line[0] == '['
    dstr = line[1:line.find(']')]
    datum['date'] = datetime.strptime(dstr, "%d/%b/%Y:%H:%M:%S +0000")
    burn, line = line.split(']', 1)
    assert line[0] == ' '
    tokens = line.split('"')
    datum['request'] = tokens[1]
    datum['request-type'], datum['request-url'], datum['request-protocol'] = \
                           datum['request'].split(" ")
    datum['status'] = tokens[2]
    datum['referrer'] = tokens[3]
    datum['useragent'] = tokens[5]
    datum['parsed-request-url'] = urlparse.urlparse(datum['request-url'])
    datum['parsed-query'] = parse_query(datum['parsed-request-url'].query)
    datum['parsed-path'] = parse_path(datum['parsed-request-url'].path)
    return datum

def parse_file(name):
    f = open(name, 'r')
    data = map(parse_line, f.readlines())
    for datum in data:
        datum['filename'] = name
    f.close()
    return data

parse_start = time.time()
data = map(parse_file, glob.glob('a8-*'))
parse_stop = time.time()

all_records = []
for datum in data:
    all_records += datum

# now analyze the data
analysis_start = time.time()
paths, queries = {}, {}
for record in all_records:
    path = record['parsed-request-url'].path
    if paths.has_key(path):
        paths[path] += 1
    else:
        paths[path] = 1
    query = record['parsed-request-url'].query
    if queries.has_key(query):
        queries[query] += 1
    else:
        queries[query] = 1

pitems = paths.items()
pitems.sort(lambda x,y: cmp(x[1],y[1]), reverse=True)
qitems = queries.items()
qitems.sort(lambda x,y: cmp(x[1],y[1]), reverse=True)

# parse out queries
parsed_queries = [q['parsed-query'] for q in all_records
                  if q['parsed-query'] is not None]
fields = [x.keys() for x in parsed_queries]
query_options = list(reduce(lambda x,y: x.union(y), map(set, fields)))

query_option_counts = {}
for opt in query_options:
    query_option_counts[opt] = 0
    for query in parsed_queries:
        if query.has_key(opt):
            query_option_counts[opt] += 1

# parse out paths
parsed_paths = [p['parsed-path'] for p in all_records
                if p['parsed-path'] is not None]
versions = [x['version'] for x in parsed_paths]
path_options = set(versions)

path_option_counts = {}
for opt in path_options:
    path_option_counts[opt] = 0
    for path in parsed_paths:
        if path['version'] == opt:
            path_option_counts[opt] += 1

# clean up variables for reporting
records_num = len(all_records)
query_strings_num = len(parsed_queries)
rest_paths_num = len(parsed_paths) # well-formed paths anyway

analysis_stop = time.time()

#for item in pitems:
#    print "%d - %s" % (item[1], item[0])
#print
#for item in qitems:
#    print "%d - %s" % (item[1], item[0])
#print
print "%d individual records" % records_num
print "%d records with '/rest' paths (%.2f%%)" % (rest_paths_num,
                                    float(rest_paths_num*100) / records_num)
print "%d records with query strings (%.2f%%)" % (query_strings_num, 
                                    float(query_strings_num*100) / records_num)
print
print "Breakdown by version:"
path_opt_items = path_option_counts.items()
path_opt_items.sort(lambda x,y: cmp(x[1],y[1]), reverse=True)
for key, value in path_opt_items:
    print "  %s: %d (%.3f%%)" % (key, value, float(value*100) / rest_paths_num)
print
print "Option counts as follows (percents out of query string total):"
query_opt_items = query_option_counts.items()
query_opt_items.sort(lambda x,y: cmp(x[1],y[1]), reverse=True)
for key, value in query_opt_items:
    print "  %s: %d (%.3f%%)" % (key, value, 
                                    float(value*100)/query_strings_num)
print
print "Parse time: %.2f seconds" % (parse_stop - parse_start)
print "Analysis time: %.2f seconds" % (analysis_stop - analysis_start)
