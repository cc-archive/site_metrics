import slogparse
import stats_aggregators as sa
import glob

def testAll():
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    aggs = list()
    aggs.append(sa.VersionAggregator())
    aggs.append(sa.ValidationAggregator())
    lp.register(aggs)

    lp.run()

    for ct, ag in enumerate(aggs):
        ag.save() # testing
        ag.showgraph()
        ag.printgraph('%(ct)i.png' % locals())

def testMetadata():
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    ag = sa.MetadataAggregator()
    lp.register(ag)

    lp.run()

    ag.save()
    ag.showgraph()


if __name__ == '__main__':
    #testAllAggregators()
    testMetadata()
