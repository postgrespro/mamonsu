#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import optparse
import re
import logging
import dateutil.parser as dateparser
import datetime as dt
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md

matplotlib.rcParams.update({'font.size': 20})

parser = optparse.OptionParser()
group = optparse.OptionGroup(parser, 'General')
group.add_option(
    '--file', '-f', dest='filename', default=None,
    help='Path to logfile')
parser.add_option_group(group)
group = optparse.OptionGroup(parser, 'Filter')
group.add_option(
    '--service', '-s', dest='service_filter', default=None,
    help='Regexp filter for service (default is no filter)')
group.add_option(
    '--from-date', dest='from_date', default=None,
    help='Filter from date (default is no filter)')
group.add_option(
    '--to-data', dest='to_date', default=None,
    help='Filter to date (default is no filter)')
parser.add_option_group(group)
group = optparse.OptionGroup(parser, 'Save')
group.add_option(
    '--directory', '-d', dest='save_dir', default='.',
    help='Save images to directory (default is current directory)')
parser.add_option_group(group)
args, _ = parser.parse_args()

logging.basicConfig(level=logging.INFO)


def parse_date(date):
    if date is None:
        return None
    try:
        date = time.mktime(
            dateparser.parse(date).timetuple())
    except:
        try:
            if date == int(float(date)):
                date = int(float(date))
        except:
            logging.error('\tUnknown date format: \'{0}\''.format(date))
            sys.exit(2)
    return date

services = {}

to_date = parse_date(args.to_date)
from_date = parse_date(args.from_date)
logging.info('\tFilter date from: {0}, to: {1}'.format(from_date, to_date))

if not os.path.isfile(args.filename):
    logging.error('\tFile \'{0}\' not found'.format(args.filename))
    sys.exit(1)
logging.info('\tOpen file {0}'.format(args.filename))
with open(args.filename, 'r') as file:
    for line in file:
        # parse
        data = line.split()
        if len(data) != 3:
            continue
        date, metric, service = data
        date, metric = float(date), float(metric)

        # filter
        if from_date is not None:
            if date < from_date:
                continue
        if to_date is not None:
            if date > to_date:
                continue
        if args.service_filter is not None:
            if not re.search(args.service_filter, service):
                continue

        # append to main hash
        if service not in services:
            services[service] = {'x': [], 'y': []}
        services[service]['x'].append(dt.datetime.fromtimestamp(date))
        services[service]['y'].append(metric)

count_services, current_service = len(services), 0
for service in services:
    current_service += 1
    ax = plt.gca()
    lines, = plt.plot(
        services[service]['x'], services[service]['y'])
    ax.set_xlabel('Date')
    ax.set_ylabel(service)
    ax.set_axis_bgcolor('white')
    ax.spines['left'].set_smart_bounds(True)
    plt.setp(lines, linewidth=4)
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.xticks(rotation=25)
    png_filename = os.path.join(
        args.save_dir,
        '{0}.png'.format(
            service.replace('/', '_').
            replace('\\', '')))
    logging.info('\t[{0}/{1}] Save {2} file: {3}'.format(
        current_service, count_services,
        service, png_filename))
    plt.savefig(png_filename)
    plt.clf()
