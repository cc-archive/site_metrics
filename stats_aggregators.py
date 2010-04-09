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
