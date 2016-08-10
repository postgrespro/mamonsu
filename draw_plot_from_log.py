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

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
except:
    logging.error('Failed to load matplotlib: fatal error, exit now.')
    sys.exit(1)

try:
    import numpy as np
    from scipy.interpolate import interp1d
    INTERPOLATION_LOADED = True
except:
    INTERPOLATION_LOADED = False

plt.rcParams.update({'font.size': 20})
plt.style.use('seaborn-white')

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
group = optparse.OptionGroup(parser, 'Picture settings')
group.add_option(
    '--interpolation-points', '-i', dest='interpolation',
    default=200, type='int',
    help='Count of interpolation points (default is 200)')
group.add_option(
    '--date-format', dest='date_format', default='%m-%d %H:%M',
    help='Count of interpolation points (default is "%m-%d %H:%M")')
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

# read file
if not os.path.isfile(args.filename):
    logging.error('\tFile \'{0}\' not found'.format(args.filename))
    sys.exit(3)
logging.info('\tOpen file {0}'.format(args.filename))
with open(args.filename, 'r') as file:
    for line in file:
        # parse line
        data = line.split()
        if len(data) != 3:
            continue
        date, metric, service = data
        date, metric = float(date), float(metric)

        # filter values
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
        services[service]['x'].append(date)
        services[service]['y'].append(metric)


count_services, current_service = len(services), 0
for service in services:
    x_axis, y_axis = services[service]['x'], services[service]['y']

    # intepolation
    if not args.interpolation == 0:
        if len(x_axis) > args.interpolation:
            if not INTERPOLATION_LOADED:
                logging.info('Interpolation load failed')
            else:
                points = zip(x_axis, y_axis)
                points = sorted(points, key=lambda point: point[0])
                x1, y1 = zip(*points)
                new_x = np.linspace(min(x1), max(x1), args.interpolation)
                new_y = interp1d(
                    x1, y1, kind='linear')(new_x)
                x_axis, y_axis = new_x, new_y

    # as datetime
    xfmt = md.DateFormatter(args.date_format)
    x_axis = [dt.datetime.fromtimestamp(x) for x in x_axis]

    # draw plot
    current_service += 1
    fig, ax = plt.subplots()
    plt.legend(loc='best', numpoints=1, fancybox=True)
    ax.plot(x_axis, y_axis, linewidth=2, linestyle=':', marker='o')
    ax.set_ylabel(service)
    ax.set_axis_bgcolor('white')
    ax.spines['left'].set_smart_bounds(True)
    ax.xaxis.set_major_formatter(xfmt)
    fig.autofmt_xdate()
    png_filename = os.path.join(
        args.save_dir,
        '{0}.png'.format(
            service.replace('/', '_').
            replace('\\', '')))
    logging.info('\t[{0}/{1}] Save {2} file: {3}'.format(
        current_service, count_services,
        service, png_filename))
    plt.savefig(png_filename, bbox_inches='tight')

    # clear memory
    fig.clf()
    plt.close(fig)
