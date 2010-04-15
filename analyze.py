import slogparse
import stats_aggregators as sa
import glob

if __name__ == '__main__':
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    aggs = list()
    aggs.append(sa.VersionAggregator())
    aggs.append(sa.ValidationAggregator())
    lp.register(aggs)

    lp.run()

    for ct, ag in enumerate(aggs):
        ag.showgraph()
        ag.printgraph('%(ct)i.png' % locals())
