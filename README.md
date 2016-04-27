## Analyze usage distribution of events in alternating bouts

This Python 3 tool calculates behavior pattern usage statistics. It works on a
CSV table where every row contains alternating bouts of either stimuli or pause
in an experiment. Each bout can span multiple time points (columns) and for each
time point in a bout, a behavior is stored. This behavior is represented by any
identifier, e.g. numbers. By default, adjacent behaviors with the same
identifier are merged, which can optionally be disabled. Next a histogram is
computed over all bouts of one type. The behavior changes within each bout are
represented as edges in a graph, each behavior is a node. It is counted how
often each node is used, which ultimately makes it possible to get a
representation percentage for each node/behavior on a particular location in a
behavior pattern.
