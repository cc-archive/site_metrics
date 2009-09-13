import logparse
import urlparse

data = logparse.load()
    # dict with: keys are 'YYYYMM', values are lists of two-tuples

# for each month,
totals = dict()
for key in data.keys():
    uris  = [urlparse.urlparse(s[1]) for s in data[key]]
    versions = [u.path.split('/')[2] for u in uris if u.path.count('/') >= 2]

    #for dstr, ustr in data[key]:
    #    if ustr.startswith('/rest/'):
    #        pieces = ustr.split('/')
    #        try:
    #            versions.append
        # dev, 1.0, 1.5
    totals[key] = {}
    for v in set(versions):
        totals[key][v] = versions.count(v)

print totals
# do some totals
# then graph them
