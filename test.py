#!/usr/bin/python
import os, sys  # get unix, python services
from stat import ST_SIZE  # or use os.path.getsize
from glob import glob  # file name expansion
from os.path import exists  # file exists test
from time import time, ctime  # time functions

print('RegTest start.')
print('user:', os.environ['USER'])  # environment variables
print('path:', os.getcwd())  # current directory
print('time:', ctime(time()), '\n')
# program = sys.argv[1]  # two command-line args
# testdir = sys.argv[2]

for test in glob(os.getcwd() + "/regression" + '/*.in'):  # for all matching input files
    f = open(test, 'r')
    line = f.readline()
    line = line.strip()
    os.system('%s %s 2>&1' % ("./mamonsu.py", line))
    os.system('diff %s.out %s.out.exp > %s.diffs' % ((test,) * 3))
    if os.stat(test + '.diffs')[ST_SIZE] == 0:
        print(
            'PASSED:', test)
        os.remove(test + '.diffs')
    else:
        print(
            'FAILED:', test, '(see %s.diffs)' % test)
    f.close()

print('RegTest done:', ctime(time()))
