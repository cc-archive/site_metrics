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

