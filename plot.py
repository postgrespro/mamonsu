#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 20})


def plot_file(filename):

    services = {}

    with open(filename, 'r') as file:
        for line in file:
            data = line.split()
            if len(data) != 3:
                continue
            date, service, metric = data
            if service not in services:
                services[service] = {'x': [], 'y': []}
            services[service]['x'].append(float(date))
            services[service]['y'].append(float(metric))

    for service in services:
        ax = plt.gca()
        lines, = plt.plot(
            services[service]['x'], services[service]['y'])
        ax.set_xlabel('Date')
        ax.set_ylabel(service)
        ax.set_axis_bgcolor('white')
        ax.spines['left'].set_smart_bounds(True)
        plt.setp(lines, linewidth=4)
        plt.show()

plot_file('/tmp/db01.ep.lux.log')
