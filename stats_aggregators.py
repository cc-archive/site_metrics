'''
Classes for aggregating data into statistics about the log files.
Each class takes care of tabulating, calculating, and then reporting
its own statistics.

Each has an 'accept' method that takes a dict of line data, pre-parsed from
the LogParser, and an identifier string.

Reporting methods are yet to be standardized.
'''


class VersionStatsAggregator:
    '''Statistics about what CC API verison is being used.

    There are three versions (1.0, 1.5, dev), and an 'invalid' entry for
    incorrect or nonexistent version information.
    '''

    def __init__(self):
        self.stats = dict()

    def accept(self, linedata, id):
        vdata = self.stats.setdefault(id, self._make_blank_version_dict())
        try:
            vstr = linedata['path'].split('/')[2] # grab the version
            if vstr not in ('1.0', '1.5', 'dev'):
                vdata['invalid'] += 1
                return
            vdata[vstr] += 1
        except IndexError:
            # version wasn't there
            vdata['invalid'] += 1

    def _make_blank_version_dict(self):
        bvd = {'1.0':0, '1.5':0, 'dev':0, 'invalid':0}
        return bvd


class ValidationAggregator:
    '''Statistics about how many queries are invalid.'''

    def __init__(self):
        self.stats = dict()
        self.valid_urls = self.build_valid_urls()

    def accept(self, linedata, id):
        vdata = self.stats.setdefault(id, {'valid':0, 'invalid':0})
        path = linedata['path']

        if path in self.valid_urls:
            vdata['valid'] += 1
        else:
            vdata['invalid'] += 1

    # TODO refactor this guy with builder functions
    def build_valid_urls(self):
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

        return set(valid_urls)
