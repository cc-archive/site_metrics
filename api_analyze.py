
g = {}

def analyze(data):
    analyze_paths(data)
    analyze_queries(data)
    generate_tree(data)
    foo(data)
    report_analysis()

def analyze_paths(data):
    g['path'] = {}
    for record in data:
        path = record['parsed-request-url'].path
        if g['path'].has_key(path):
            g['path'][path] += 1
        else:
            g['path'][path] = 1

    g['path']['items'] = g['path'].items()
    g['path']['items'].sort(_item_sort, reverse=True)

def analyze_queries(data):
    g['query'] = {}
    for record in data:
        query = record['parsed-request-url'].query
        if g['query'].has_key(query):
            g['query'][query] += 1
        else:
            g['query'][query] = 1

    g['query']['items'] = g['query'].items()
    g['query']['items'].sort(_item_sort, reverse=True)

def validate_paths(paths):
    # do nothing for now
    return paths


def generate_tree(data):
    tree = {}
    
    paths = [p['parsed-request-url'].path.split('/') for p in data
                    if p['parsed-path'] is not None]
    
    # validate paths
    valid_paths = validate_paths(paths)
    
    
    g['tree'] = tree

def foo(data):
    # parse out queries
    parsed_queries = [q['parsed-query'] for q in data
                  if q['parsed-query'] is not None]
    fields = [x.keys() for x in parsed_queries]
    query_options = list(reduce(lambda x,y: x.union(y), map(set, fields)))

    query_option_counts = {}
    for opt in query_options:
        query_option_counts[opt] = 0
        for query in parsed_queries:
            if query.has_key(opt):
                query_option_counts[opt] += 1

    # parse out paths
    parsed_paths = [p['parsed-path'] for p in data
                    if p['parsed-path'] is not None]
    versions = [x['version'] for x in parsed_paths]
    path_options = set(versions)

    path_option_counts = {}
    for opt in path_options:
        path_option_counts[opt] = 0
        for path in parsed_paths:
            if path['version'] == opt:
                path_option_counts[opt] += 1

    # clean up variables for reporting
    g['records_num'] = len(data)
    g['query_strings_num'] = len(parsed_queries)
    g['query_strings_pct'] = float(g['query_strings_num']*100) / g['records_num']
    g['rest_paths_num'] = len(parsed_paths) # well-formed paths anyway
    g['rest_paths_pct'] = float(g['rest_paths_num']*100) / g['records_num']

def report_analysis():
    for key, value in g['path']['items']:
        print "%s -- %s" % (key, value)

def _item_sort(x,y):
    return cmp(x[1],y[1])
