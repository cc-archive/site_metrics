import glob
from datetime import datetime
import urlparse

# what level should date-filtering happen at?
# probably the file level

# TODO add ability to break output files by month or year

def _parse_line(line): # grab the two fields from log files
    datestr = line[15:35] # hard code for speed
    urlstr = line.split('"',2)[1].split(' ')[1]
    return (datestr, urlstr)

def _parse_file(name):
    f = open(name, 'r')
    data = map(_parse_line, f.readlines())
    f.close()
    return data

def parse():
    filenames = glob.glob('a8-*') # TODO more specificity
    data = map(_parse_file, filenames)
    data = reduce(lambda x,y: x + y, data, [])
    return data

def dump(data):
    f = open('paths.txt','w')
    for datum in data:
        f.write('%s %s\n' % datum)
    f.close()

def load():
    f = open('paths.txt','r')
    return [tuple(line.split(' ')) for line in f.readlines()]

def process(data):
    return [(datetime.strptime(datum[0], '%d/%b/%Y:%H:%M:%S'),
             urlparse.urlparse(datum[1]))
            for datum in data]

if __name__ == '__main__':
    import time
    
    parse_start = time.time()
    data = parse()
    parse_stop = time.time()

    old_len = len(data)

    dump_start = time.time()
    dump(data)
    dump_stop = time.time()

    del data

    load_start = time.time()
    data = load()
    load_stop = time.time()
    
    assert old_len == len(data)
    
    process_start = time.time()
    data = process(data)
    process_stop = time.time()

    print "Parsing: %.2f seconds" % (parse_stop - parse_start)
    print "Dumping: %.2f seconds" % (dump_stop - dump_start)
    print "Loading: %.2f seconds" % (load_stop - load_start)
    print "Processing: %.2f seconds" % (process_stop - process_start)
