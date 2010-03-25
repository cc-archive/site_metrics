import glob
import gzip
import urlparse
import csv

'''
File name is short for "serial log parse". Instead of trying to parse all the logs at once, analyze and collect data on the first pass. This way should be faster and use much less memory. The downside is that adding new charts will necessarily change this parser.
'''

class LogfileStats: 
    '''LogfileStats takes care of gathering all the important information
       in a log file, by accepting one line at a time through the parse_line
       method. 
       Reporting formats aren't standardized yet.
    '''
    def __init__(self, fn):
        self._name = self._name_from_fn(fn)
        self._raw_data = []
        self._processed_data = {}

    def parse_line(self, line):
        datum = dict() # all the information about this particular line
        urlstr = line.split('"',2)[1].split(' ')[1] # url the client asked for
        url = urlparse.urlparse(urlstr)
        # path and query are the items of interest

        # TODO: fiddle with it here, get some data to come out
        # TODO: then write graphers for this data!
        path = url.path
        qdict = self._query2dict(url.query)

        ### Record version information
        datum['version'] = None
        try:
            v = path.split('/')[2] # grab the version
            if v not in ('1.0','1.5','dev'):
                v = 'invalid'
            datum['version'] = v
        except IndexError:
            # version information wasn't there
            datum['version'] = 'nonexistent'

        self._raw_data.append(datum)

    def finalize(self):
        '''Processes the raw data into formatted results'''
        ### Tally version information
        vinfo = {'1.0':0, '1.5':0, 'dev':0, 'invalid':0, 'nonexistent':0}
        for d in self._raw_data:
            vinfo[d['version']] += 1
        self._processed_data['versions'] = vinfo

    def _query2dict(self, query):
        '''Helper function to turn the 'query' field returned by urlparse
        into a dictionary'''
        qdict = dict()
        if query == '':
            return qdict
        qlist = query.split('&')
        if qlist.count('') > 1:
            raise Exception('Expected no more than one empty string' +
                            ' creating query dictionary')
        elif qlist.count('') == 1:
            qlist.remove('')
        
        for item in qlist:
            kv = item.split('=')
            if len(kv) != 2: # due to weird query string. possibly invalid.
                qdict[kv[0]] = None
            else:
                qdict[kv[0]] = kv[1]

        return qdict

    def _name_from_fn(self, fn):
        ymdstr = fn.split('/')[1].split('.')[0] # string format YYYYMMDD
        return '%(year)s-%(month)s-%(day)s' % {'year':ymdstr[:4],
                                               'month':ymdstr[4:6],
                                               'day':ymdstr[-2:]}

def parse_logfiles():
    stats = [] # a list of LogfileStats
    filenames = glob.glob('logs/*.gz')
    for fn in filenames:
        lfs = LogfileStats(fn) # make a stats log for each file
        f = gzip.open(fn, 'r')
        for line in f.readlines():
            lfs.parse_line(line) # the stats log parses each line in its file
        lfs.finalize()
        stats.append(lfs)
    stats.sort(lambda x,y: cmp(x._name, y._name))
    return stats

def write_stats(stats):
    # assume stats is sorted
    f = open('versiondata.csv','w')
    writer = csv.writer(f)

    writer.writerow(['date','nonexistent','invalid','1.0','1.5','dev'])
    for stat in stats:
        vs = stat._processed_data['versions']
        row = [stat._name, vs['nonexistent'], vs['invalid'],
                           vs['1.0'], vs['1.5'], vs['dev']]
        writer.writerow(row)
    f.close()

def read_stats():
    f = open('versiondata.csv','r')
    reader = csv.reader(f)

    reader.readrow() # first line
    return reader.readrows() # a cop out? maybe.


if __name__ == '__main__':
    stats = parse_logfiles()
    for guy in stats:
        print guy._name
    write_stats(stats)
