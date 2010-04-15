import slogparse
import stats_aggregators as sa
import glob

if __name__ == '__main__':
    fns = glob.glob('logs/*.gz')
    lp = slogparse.LogfileParser(fns)

    ag = sa.VersionStatsAggregator()
    lp.register(ag)

    lp.run()

    print ag
