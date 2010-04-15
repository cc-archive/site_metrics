import glob
import gzip
from datetime import datetime
import urlparse

# TODO add ability to break output files by month or year

class lazy_dict(dict):
    """Dictionary to lazy-load pre-parsed log files."""
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        self._fns = glob.glob('paths*.gz')

    def __getitem__(self, key):
        pass

def _parse_line(line): # grab the two fields from log files
    datestr = line[15:35] # hard code for speed
    urlstr = line.split('"',2)[1].split(' ')[1]
    return (datestr, urlstr)

def _parse_file(name):
    f = gzip.open(name, 'r')
    data = map(_parse_line, f.readlines())
    f.close()
    return data

def _group_filenames(filenames):
    """Takes a list of file names, returns a dictionary of file names
    broken up by year and month."""
    grp = dict()
    for n in filenames:
        ym = n[n.rfind('\\')+1:-5] # year and month; TODO fix this in production
        if not grp.has_key(ym):
            grp[ym] = [n]
        else:
            grp[ym].append(n)
    return grp

def parse():
    filenames = glob.glob('logs/*.gz') # TODO fix in production
    grouped_fns = _group_filenames(filenames)
    data = dict()
    for key, value in grouped_fns.items():
        tmp = map(_parse_file, value)
        data[key] = reduce(lambda x,y: x + y, tmp, [])
    return data

def dump(data):
    for key, value in data.items():
        f = gzip.open('paths%s.gz' % key, 'w')
        for datum in value:
            f.write('%s %s\n' % datum)
        f.close()

def load(): # TODO introduce lazy load evaluation
    """Globs all pre-parsed gzipped log files, reads them in,
    and makes them accessible as a dict of lists of two-tuples."""
    #data = lazy_dict()
    fns = glob.glob('paths*.gz')
    data = dict()
    for name in fns:
        ym = name[5:-3] # Year and month in YYYYMM format
        f = gzip.open(name,'r')
        data[ym] = [tuple(line.split(' ')) for line in f.readlines()]
        f.close()
    return data

def process(data): # note this can't take the result of load() directly
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
    #data = process(data) # TODO fix this
    process_stop = time.time()

    print "Parsing: %.2f seconds" % (parse_stop - parse_start)
    print "Dumping: %.2f seconds" % (dump_stop - dump_start)
    print "Loading: %.2f seconds" % (load_stop - load_start)
    print "Processing: %.2f seconds" % (process_stop - process_start)
