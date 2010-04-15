import slogparse
import stats_aggregators as sa
import glob

if __name__ == '__main__':
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    aggs = list()
    aggs.append(sa.VersionStatsAggregator())
    aggs.append(sa.ValidationAggregator())
    lp.register(aggs)

    lp.run()

    print ag
