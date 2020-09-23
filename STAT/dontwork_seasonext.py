#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request

__version__ = '0.1.0'

def getData(url, data=None):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            print('Request failed.', file=sys.stderr)
            print('Reason: ', e.reason, file=sys.stderr)
        if hasattr(e, 'code'):
            print('Error code: ', e.code, file=sys.stderr)
            sys.exit(1)
    else:
        # everything is fine
        return response.read().decode('utf-8')

def fixPGN(pgn, r, s):
    event = 'Event "Lichess4545 League Season {0}"'.format(s)
    round_ = 'Round "{0}"'.format(r)
    pgn = pgn.replace('Round "-"', round_)
    p = re.compile('Event "[\w ]+"')
    pgn = p.sub(event, pgn)
    return pgn

def getPGN(args):
    datafile = "season" + str(args.season) + "pgns.pgn"
    outfile = open(datafile, 'w')
    clocks = 'false' if args.noclocks else 'true'
    rounds = args.roundsmax + 1
    for r in range(1, rounds):
        url = 'https://www.lichess4545.com/team4545/season/{0}/round/{1}/pairings/'.format(args.season, r)
        html = getData(url)
        if html:
            links = re.findall(r'en\.lichess\.org\/([\w]+)', html) # get game links
            if len(links) > 0:
                url = 'https://lichess.org/games/export/_ids?clocks={0}&opening=true'.format(clocks)
                data = ','.join(links)
                pgn = getData(url, data.encode('utf-8'))
                outfile.write(fixPGN(pgn, r, args.season))
                time.sleep(5) # wait 5 seconds before requesting next round

def main():
    # setup parser for command-line arguments
    parser = argparse.ArgumentParser(description='Lichess4545 League PGN exporter')
    group_r = parser.add_argument_group('required arguments')
    group_r.add_argument('-s', '--season', help='season number', type=int, metavar='NUM', required=True)
    parser.add_argument('--noclocks', help='don\'t include clock comments', action='store_true')
    parser.add_argument('--roundsmax', help='max number of rounds, default=8', type=int, metavar='NUM', default=8)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()

    try:
        getPGN(args)
    except KeyboardInterrupt:
        print('Program terminated at user request.', file=sys.stderr)

if __name__ == '__main__':
    main()