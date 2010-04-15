import logparse
import urlparse

data = logparse.load()
    # dict with: keys are 'YYYYMM', values are lists of two-tuples

# for each month,
totals = dict()
for key in data.keys():
    uris  = [urlparse.urlparse(s[1]) for s in data[key]]
    versions = [u.path.split('/')[2].rstrip()
                for u in uris if u.path.count('/') >= 2]

    #for dstr, ustr in data[key]:
    #    if ustr.startswith('/rest/'):
    #        pieces = ustr.split('/')
    #        try:
    #            versions.append
        # dev, 1.0, 1.5
    totals[key] = dict()
    for v in set(versions):
        totals[key][v] = versions.count(v)

# the only keys that should matter are:

valid = ('dev','1.5','1.0')
for key, value in totals.items():
    print '%s:' % key
    for v in valid:
        print '  %s - %d' % (v, value[v])
    invalid_count = 0
    for key2, value2 in value.items():
        if key2 not in valid:
            invalid_count += value2
    print '  invalid - %d' % invalid_count


# do some totals
# then graph them
