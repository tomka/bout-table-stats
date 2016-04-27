#!/usr/bin/python
#
# This tool works on a table where every row is associated with one
# individual larva, referenced in the first column. The other columns
# represent time points, each being either part of a sensation period or
# a pause. Starting with a 

import argparse
import csv
import logging
import pprint

from itertools import groupby


# Get an instance of a logger and attach a console handler to it
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.addHandler(ch)

parser = argparse.ArgumentParser(description="calculate pattern"
        "historgram in stimuli bouts")
parser.add_argument("-pf", "--pause-first", action="store_true",
        default=False, help="The first bout is a pause")
parser.add_argument("-nm", "--no-merge", action="store_true",
        default=False, help="Set if adjacent same behaviors in bouts shouldn't be combined")
parser.add_argument("-o", "--offset", type=int, default=1,
        help="The column offset to the first bout")
parser.add_argument("-d", "--delim", type=str,
        help='Delimiter in CSV file', default=";")
parser.add_argument("-hr", "--head-rows", type=int,
        help='Number of header rows in CSV file', default=1)
parser.add_argument("-l", "--log", type=str, choices=['error', 'warning', 'info', 'debug'],
        help='Number of header rows in CSV file', default='info')
parser.add_argument("-n", "--max-rows", type=int, default=None,
        help="Limit the number of rows to read fom the input file")
parser.add_argument("s", type=int, help="the number of stimuli columns")
parser.add_argument("p", type=int, help="the number of pause columns")
parser.add_argument("file", type=str, help="the CSV file to load")

def create_histograms(s, p, path, offset=1, begin_with_stimuli=True,
        delim=';', nheadrows=1, nomerge=False, max_rows=None):

    logger.info("Creating pattern histograms beginning with {} bout in file: {}" \
        .format('stimuli' if begin_with_stimuli else 'pause', path))
    logger.info("Stimuli bout length: {} Pause bout length: {}".format(s, p))

    # Load CSV and collect stimuli and pause bouts
    head_rows = []
    raw_stimuli = []
    raw_pauses = []
    with open(path, 'r') as csvfile:
        linereader = csv.reader(csvfile, delimiter=delim)
        stimuli_bout = begin_with_stimuli
        current_loc = offset
        for n, row in enumerate(linereader):
            if n < nheadrows:
                head_rows.append(row)
                continue
            if max_rows and n + nheadrows >= max_rows:
                logger.info("Reached row limit of {} rows".format(max_rows))
                break
            # Collect all bouts
            n_stimuli_bouts = 0
            n_pause_bouts = 0
            logger.debug("Row: {}".format(row))
            while True:
                start = offset + s * n_stimuli_bouts + p * n_pause_bouts
                length = s if stimuli_bout else p
                raw_bout = row[start:(start + length)]

                # Merge adjacent bout elements if they are the same, if not disabled
                bout = tuple(raw_bout if nomerge else [k for k,v in groupby(raw_bout)])
                logger.debug("Bout start: {} bound end: {} Bout: {}" \
                        .format(start, start + length - 1, ",".join(bout)))

                # If we can't get enough content anymore, stop
                if length != len(raw_bout):
                    break

                if stimuli_bout:
                    raw_stimuli.append(bout)
                    n_stimuli_bouts += 1
                else:
                    raw_pauses.append(bout)
                    n_pause_bouts += 1

                stimuli_bout = not stimuli_bout

    logger.info("Found {} stimuli bouts in total".format(len(raw_stimuli)))
    logger.info("Found {} pause bouts in total".format(len(raw_pauses)))

    # Build stimuli and pause histograms. Each histogram is a list of
    # bout positions. Each bout position is a dictionary mapping a
    # seen value to the number of times it has been seen in the list of
    # bouts.
    stimuli_histogram = make_histogram(raw_stimuli)
    pause_histogram = make_histogram(raw_pauses)

    stimuli_ptree = percentage_tree(stimuli_histogram)
    pause_ptree = percentage_tree(pause_histogram)

    logger.debug("Stimuli histogram: \n{}".format(format_histogram(stimuli_ptree)))
    logger.debug("Pause histogram: \n{}".format(format_histogram(pause_ptree)))

def percentage_tree(histogram):
    return histogram
    def walk(nodes):
        level = {}
        for n in nodes:
            # Get percentage of node count vs total count on this level
            total = 0
            for e,p in nodes.iteritems():
                total += p.count
            nodes = nodes.get('children')

    return walk(histogram)

def format_histogram(histogram):
    return pprint.pformat(histogram, indent=0)

def make_histogram(bouts):
    root = dict()
    for bout in bouts:
        parent = root
        for b in bout:
            node = parent.get(b)
            if node is None:
                node = {
                    'count': 0,
                    'children': dict()
                }
                parent[b] = node
            node['count'] += 1
            parent = node['children']

    return root

if __name__ == '__main__':
    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper())
    logger.setLevel(loglevel)
    ch.setLevel(loglevel)

    create_histograms(args.s, args.p, args.file, args.offset, not
            args.pause_first, args.delim, args.head_rows, args.no_merge,
            args.max_rows)