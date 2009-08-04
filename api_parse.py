import glob
from datetime import datetime
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
    # hack
    if len(pieces) < 3:
        return dict(version='None', call=['None'])
    return dict(version=pieces[2], call=pieces[3:])

def parse_line(line):
    datum = {}
    line = line[len("127.0.0.1 - - "):] # chop off beginning
    assert line[0] == '['
    datum['datestr'] = line[1:line.find(']')]
    burn, line = line.split(']', 1)
    assert line[0] == ' '
    tokens = line.split('"')
    datum['request'] = tokens[1]
    datum['request-type'], datum['request-url'], datum['request-protocol'] = \
                           datum['request'].split(" ")
    #datum['status'] = tokens[2]
    #datum['referrer'] = tokens[3]
    #datum['useragent'] = tokens[5]
    return datum

def process_item(item):
    item['parsed-request-url'] = urlparse.urlparse(item['request-url'])
    item['parsed-query'] = parse_query(item['parsed-request-url'].query)
    item['parsed-path'] = parse_path(item['parsed-request-url'].path)
    item['datetime'] = datetime.strptime(item['datestr'],
                                         "%d/%b/%Y:%H:%M:%S +0000")
    return item

def parse_file(name):
    f = open(name, 'r')
    data = map(parse_line, f.readlines())
    for datum in data:
        datum['filename'] = name
    f.close()
    return data

def parse():
    data = map(parse_file, glob.glob('a8-*')) # "a8-api.creativecommons.org-access.log-20081003"]) #
    all_records = []
    for datum in data:
        all_records += datum
    return all_records

def minimal_parse():
    return [(x['datestr'], x['request-url']) for x in parse()]

def process(records):
    return map(process_item, records)

def run():
    return process(parse())

if __name__ == '__main__':
    import time

    parse_start = time.time()
    data = parse()
    parse_stop = time.time()

    #length = len(repr(data))

    process_start = time.time()
    data = process(data)
    process_stop = time.time()

    print "Parsing took %.2f seconds" % (parse_stop - parse_start)
    print "Processing took %.2f seconds" % (process_stop - process_start)
    #print "Length: %d" % length
    #print "Data representation is %d characters long" % len(repr(data))
