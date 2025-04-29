#!python
import os
import traceback
import sys

# decorator to run a function only once
# https://stackoverflow.com/a/4104188
# add @run_once
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))

def loadfile(filepath, lines = False):
    with open(filepath) as f:
        text = f.read()
        if lines:
            return text.split('\n')
        return text

def ls_files(rootdir, ext=[]):
    allfiles = []
    #Recursive function to walk through the codebase
    for root, dirs, files in os.walk(rootdir , topdown=False):
        for name in files:
            fname = os.path.join(root, name)
            if ext is None or len(ext) == 0:
                allfiles.append(fname)
            elif name[name.rfind('.'):] in ext:
                allfiles.append(fname)
    allfiles.sort()
    return allfiles

def print_exception():
    traceback.print_exc()

def print_track_trace():
    traceback.print_stack()

def is_number(num):
    try:
        float(num)
        return True
    except:
        return False