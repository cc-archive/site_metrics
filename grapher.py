'''Standardize graphing of metrics data held in CSV files.
'''

import pylab
import csv

class Grapher:

    def graph(self, csv_filename):
        '''Takes a csv filename and prints a graph with its data.
        First line of file contains titles of data series.'''
        f = open(csv_filename, 'r')
        r = csv.reader(f)

        titles = r.next()
        series = [ list() for t in titles ]

        for line in r:
            for i, val in enumerate(line):
                series[i].append(val) # might be str not int

        index = titles.pop(0)
        dates = series.pop(0)
        x = range(len(dates))

        # graph it up
        for title, data in zip(titles, series):
            pylab.plot(x, data, label=title)
        pylab.legend(loc='best')
        pylab.show()


if __name__ == '__main__':
    g = Grapher()

    g.graph('versiondata.csv')
