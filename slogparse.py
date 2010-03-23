import glob
import gzip
import urlparse

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
        self._name = fn.split('/')[1].split('.')[0] # string format YYYYMMDD
        self._num_lines = 0

    def parse_line(self, line):
        urlstr = line.split('"',2)[1].split(' ')[1] # url the client asked for
        url = urlparse.urlparse(urlstr) # XXX some exception to catch here?
        self._num_lines += 1
        # path and query are the items of interest
        path = url.path
        qdict = self._query2dict(url.query)
        print path

    def _query2dict(self, query):
        if query == '':
            return dict()
        qlist = query.split('&')
        if qlist.count('') > 1:
            raise Exception('Expected no more than one empty string' +
                            ' creating query dictionary')
        elif qlist.count('') == 1:
            qlist.remove('')
        try:
            return dict([item.split('=') for item in qlist])
        except ValueError:
            print 'INVALID' # handle this later
            return dict()

if __name__ == '__main__':
    stats = [] # a list of LogfileStats
    filenames = glob.glob('logs/*.gz')
    filenames = [ filenames[0] ] # HACK for speed
    for fn in filenames:
        lfs = LogfileStats(fn) # make a stats log for each file
        f = gzip.open(fn, 'r')
        for line in f.readlines():
            lfs.parse_line(line) # the stats log parses each line in its file
        stats.append(lfs)
