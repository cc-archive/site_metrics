from matplotlib.pyplot import *
import slogparse

if __name__ == '__main__':
    stats = slogparse.parse_logfiles()
    dates = [stat._name for stat in stats] # get the dates
    graphs = ['nonexistent', '1.0', '1.5', 'dev', 'invalid' ]
    for graph in graphs:
        plot([stat._processed_data['versions'][graph] for stat in stats],
              label=graph)
    legend()
    show()
