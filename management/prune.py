"""
Deletes all log files older than a set number of days.
Specify a list of log file locations in a file called "manage_these_logs" and
place it in this folder.
The list of logs can have wildcards, and follows the unix pattern matching
rules.

E.g.
/var/log/hoglundi/*.err*

By default, this script does a dry run.  To actually get it to delete files
you have to give the argument "really_do_it"

E.g. 
python prune.py really_do_it


"""

import glob
import os
import time
import sys

dry_run = True
try:
    dry_run = sys.argv[1] != 'really_do_it'
except IndexError:
    pass

here = os.path.split(os.path.realpath(__file__))[0]

allowed_age = 90 #days
allowed_age *= 60*60*24  #convert to seconds

with open(os.path.join(here, "manage_these_logs")) as f:
    paths = f.readlines()

for path in paths:
    path = path.strip()
    folder = os.path.split(path)[0]
    files = glob.glob(path)
    for logfile in files:
        full_path = os.path.join(folder, logfile)
        last_modified = os.path.getmtime(full_path)
        age = time.time() - last_modified
        if age > allowed_age:
              print 'delete: ', full_path
              if not dry_run:
                  os.remove(full_path)


if dry_run:
    print 'dry run complete'
