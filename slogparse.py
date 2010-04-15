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

    def __init__(self, log_filenames, gzip=True):
        assert hasattr(log_filenames, '__iter__')
        # make sure you can iterate over the filenames

        self.aggregators = []
        self.log_fns = log_filenames
        self.gzipped_files = gzip

    def register(self, statsaggregator):
        if hasattr(statsaggregator, '__iter__'):
            self.aggregators.extend(statsaggregator)
        else:
            self.aggregators.append(statsaggregator)

    def create_id_from_filename(self, filename):
        '''Helper function: take a filename and return an identifier
           derived from that filename. Highly contingent on getting a
           filename in the right format.'''
        ymdstr = filename.split('/')[1].split('.')[0] # string format YYYYMMDD
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

        #print locals() #DEBUG
        return locals() # this is awesome but watch for bugs

    def run(self):
        for fn in self.log_fns:
            id = self.create_id_from_filename(fn)

            if self.gzipped_files:
                open = gzip.open # shadows 'open', local scope only i hope
            f = open(fn, 'r')
            for line in f.readlines():
                linedata = self.process_line(line)
                for ag in self.aggregators:
                    ag.accept(linedata, id)


if __name__ == '__main__':
    # TODO maybe some unit tests here
    lfp = LogfileParser(['foo.txt','bar.txt'])
