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

    for i, ag in enumerate(aggs):
        ag.save_csv('%i.csv' % i)

def testMetadata():
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    ag = sa.MetadataAggregator()
    lp.register(ag)

    lp.run()


if __name__ == '__main__':
    testAll()
    #testMetadata()
