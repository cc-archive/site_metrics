from matplotlib.pyplot import *
import slogparse
from math import log

if __name__ == '__main__':
    inlogs = True
    stats = slogparse.read_stats()
    fields = ['date','nonexistent','invalid','1.0','1.5','dev']

    ddicts = []
    for row in stats:
        ddict = dict()
        for i, field in zip(range(len(fields)), fields):
            ddict[field] = row[i]
        ddicts.append(ddict)

    # sort just in case
    ddicts.sort(lambda x,y: cmp(x['date'], y['date']))

    graphs = ['nonexistent', '1.0', '1.5', 'dev', 'invalid']
    for graph in graphs:
        if inlogs:
            plot([log(float(ddict[graph]),10) for ddict in ddicts], label=graph)
        else:
            plot([ddict[graph] for ddict in ddicts], label=graph) 
    legend()
    show()
