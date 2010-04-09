import glob
import gzip
import urlparse
import csv

'''
File name is short for "serial log parse". Instead of trying to parse all the logs at once, analyze and collect data on the first pass. This way should be faster and use much less memory.

The parser will use a listener-type design pattern to register "statistics" objects that take care of calculating and reporting statistics. This way the log parser doesn't have to change every time we add new reporting.
'''

class LogfileParser:
    '''Takes a list of file names to parse. User then registers a number of 
       StatsAggregator objects, which will accept one line at a time from
       the log files, along with an identifier of which file / day / time
       period the line corresponds to. 
    '''

    def __init__(self, log_filenames):
        assert hasattr(log_filenames, '__iter__')
        # make sure you can iterate over the filenames

        self.aggregators = []
        self.log_fns = log_filenames

    def register(self, statsaggregator):
        self.aggregators.append(statsaggregator)

    def create_id_from_filename(self, filename):
        '''Helper function: take a filename and return an identifier
           derived from that filename. Highly contingent on getting a
           filename in the right format.'''
        ymdstr = fn.split('/')[1].split('.')[0] # string format YYYYMMDD
        year = ymdstr[:4]
        month = ymdstr[4:6]
        day = ymdstr[-2:]
        return '%(year)s-%(month)s-%(day)s' % locals()

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
        elif qlist.count('') == 1: # TODO better way to handle this?
            qlist.remove('')
        
        for item in qlist:
            kv = item.split('=')
            if len(kv) != 2: # due to weird query string. possibly invalid.
                qdict[kv[0]] = None
            else:
                qdict[kv[0]] = kv[1]

        return qdict

    def process_line(self, line):
        urlstr = line.split('"',2)[1].split(' ')[1] # url the client asked for
        url = urlparse.urlparse(urlstr)
        # path and query are the items of interest

        path = url.path
        qdict = self._query2dict(url.query)

        print locals() #DEBUG
        return locals() # this is awesome but watch for bugs

    def run(self):
        for fn in self.log_fns:
            id = self.create_id_from_filename(fn)

            with open(fn, 'r') as f:
                for line in f.readlines():
                    linedata = self.process_line(line)
                    for ag in self.aggregators:
                        ag.accept(linedata, id)

class LogfileStats: 
    '''This guy is DEPRECATED. We are just using him for parts.

       LogfileStats takes care of gathering all the important information
       in a log file, by accepting one line at a time through the parse_line
       method. 
       Reporting formats aren't standardized yet.
    '''
    def __init__(self, fn):
        self._name = self._name_from_fn(fn)
        self._raw_data = []
        self._processed_data = {}
        self._valid_urls = set(self._build_valid_urls())

    def parse_line(self, line):
        datum = dict() # all the information about this particular line
        urlstr = line.split('"',2)[1].split(' ')[1] # url the client asked for
        url = urlparse.urlparse(urlstr)
        # path and query are the items of interest

        path = url.path
        qdict = self._query2dict(url.query)

        ### Record validation information
        datum['valid'] = path in self._valid_urls

        # debugging
        #if not datum['valid'] and 'dev' in path:
        #    print urlstr

        self._raw_data.append(datum)

    def finalize(self):
        '''Processes the raw data into formatted results'''
        ### Tally version information
        vinfo = {'1.0':0, '1.5':0, 'dev':0, 'invalid':0, 'nonexistent':0}
        for d in self._raw_data:
            vinfo[d['version']] += 1
        self._processed_data['versions'] = vinfo
 
        ### Tally valid url information
        self._processed_data['valid'] = len(filter(lambda x: x['valid'], 
                                            self._raw_data))
        self._processed_data['invalid'] = len(filter(lambda x: not x['valid'],
                                              self._raw_data))

    # TODO refactor this guy with builder functions
    def _build_valid_urls(self):
        '''Create and return a list of 'valid' urls that can
        be called on the CC API.'''

        # TODO is it cheaper to extend lists or add them?
        preurls = list()
        classes = ('standard', 'publicdomain', 'recombo')
        r = 'rest'

        # 1.0 api calls
        b = '1.0'
        preurls.append([r, b])
        preurls += [ ['', r, b, 'license', c] for c in classes]
        preurls += [ ['', r, b, 'license', c, 'issue'] for c in classes]

        # 1.5 api calls
        b = '1.5'
        preurls.append(['', r, b])
        preurls += [ ['', r, b, s] for s in ('locale', 'classes')]
        preurls += [ ['', r, b, 'license', c] for c in classes]
        preurls += [ ['', r, b, 'license', c, 'issue'] for c in classes]
        preurls += [ ['', r, b, 'license', c, 'get'] for c in classes]
        preurls.append(['', r, b, 'details'])
        preurls.append(['', r, b, 'simple', 'chooser'])
        preurls.append(['', r, b, 'support', 'jurisdictions'])

        # dev api calls
        b = 'dev'
        # ...
        preurls.append(['', r, b, 'support', 'jurisdictions'])
        preurls.append(['', r, b, 'support', 'jurisdictions.js'])

        def add_space(*ls): # there's got to be a better way
            nl = list(ls)
            nl.append('')
            return nl

        preurls += [add_space(*p) for p in preurls]
        valid_urls = ['/'.join(p) for p in preurls]

        return valid_urls



''' These functions are probably DEPRECATED.'''

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

    ### Write version information
    with open('versiondata.csv','w') as f:
        writer = csv.writer(f)

        writer.writerow(['date','nonexistent','invalid','1.0','1.5','dev'])
        for stat in stats:
            vs = stat._processed_data['versions']
            row = [stat._name, vs['nonexistent'], vs['invalid'],
                               vs['1.0'], vs['1.5'], vs['dev']]
            writer.writerow(row)
        f.close()

    ### Write valid urls information
    with open('validdata.csv','w') as f:
        writer = csv.writer(f)

        writer.writerow(['date','valid','invalid'])
        for stat in stats:
            vd = stat._processed_data['valid']
            ivd = stat._processed_data['invalid']
            writer.writerow([stat._name, vd, ivd])
        f.close()
   

def read_stats():
    f = open('versiondata.csv','r')
    reader = csv.reader(f)

    reader.next() # first line
    return [line for line in reader] # maybe a copout


if __name__ == '__main__':
    # TODO maybe some unit tests here
    lfp = LogfileParser(['foo.txt','bar.txt'])
