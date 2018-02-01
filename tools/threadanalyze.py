#!/usr/bin/env python

import argparse
import subprocess
import re
import sys
import multiprocessing

class ThreadInfo:

    def __init__(self):
        self.name = ''
        self.num  = 0
        self.state = 'active'
        self.type = ''
        self.bt = []

    def summary(self, bt_size = 0):
        s = ['Thread - {} -[type:{} state:{}]'.format(self.num, self.type, self.state)]
        if bt_size > 0:
            s.extend(self.bt[:bt_size])
        else:
            s.extend(self.bt)
        return '\n'.join(s)

    def __repr__(self):
        s = ['Thread - {} -[type:{} state:{}]'.format(self.num, self.type, self.state)]
        s.extend(self.bt)
        return '\n'.join(s)

class ThreadAnalyzer:

    def __init__(self,process_name, thread_num, pattern, btsize):
        self.threads = dict()
        self.types = {}
        self.states = {}
        self.numPrinted = 0
        self.bt_size = btsize
        self.thread_num = thread_num
        self.process_name = process_name
        self.pattern = None
        if pattern:
            self.pattern = re.compile(pattern)

        
    def process(self):
        cmd = 'gdb --batch --ex "thread apply {} bt" -p $(pgrep {})'.format(self.thread_num, self.process_name)
        bt = subprocess.check_output(cmd, shell = True).split('\n')
        p_str = 'Thread ([0-9]+) .*'
        pat = re.compile(p_str)

        tInfo = None
        for line in bt:
            if len(line) == 0: continue
            m = pat.match(line)
            if m:
                tInfo = ThreadInfo()
                tInfo.num = int(m.groups()[0])
                tInfo.name = line
                tInfo.bt = []
                self.threads[tInfo.num] = tInfo
            elif tInfo:
                # dont add anymore bt for this thread
                if len(tInfo.type) > 0: continue

                # identify state
                if len(tInfo.bt) <= 1 and '_lock_wait ' in line:
                    tInfo.state = 'lock'
                    
                elif len(tInfo.bt) <= 1 and (' pthread_cond_timedwait@' in line
                                             or ' pthread_cond_wait@' in line
                                             or ' epoll_wait' in line
                                             or 'poll ' in line):
                    tInfo.state = 'wait'

                # identify type
                if 'memcached_main ()' in line:
                    tInfo.type = 'main'                
                elif 'ExecutorThread::run()' in line or 'Executor::run()' in line:
                    tInfo.type = 'executor'
                elif 'MemoryTracker::statsThreadMainLoop' in line:
                    self.memTrackerThread = tInfo.num
                    tInfo.type = 'stats'
                elif 'worker_libevent' in line:
                    tInfo.type = 'event'
                elif 'consume_events' in line:
                    tInfo.type = 'audit'
                elif 'logger_thread_main' in line:
                    tInfo.type = 'logger'
                elif 'check_stdin_thread' in line:
                    tInfo.type = 'stdin'

                tInfo.bt.append(line)
        # end for
        # now process
        
        numThreads = len(self.threads)
        for num,t in self.threads.iteritems():
            self.types[t.type] = self.types.get(t.type,{})
            self.types[t.type][t.state] = self.types[t.type].get(t.state,0)
            self.types[t.type][t.state] += 1
            self.states[t.state] = self.states.get(t.state,0)
            self.states[t.state] += 1
        
        
    def summary(self):
        numThreads = len(self.threads)
        numCores = multiprocessing.cpu_count()
        states = str(self.states)
        states = states.replace('\'','').replace(' ','').strip('{}')

        print 'cores={} '.format(numCores),
        if len(self.states) > 1:
            print 'threads: total=[{}: {}]'.format(len(self.threads), states),
        else:
            print 'threads: total=[{}]'.format(states),
        for th_type in sorted(self.types.keys()):
            states = str(self.types[th_type])
            states = states.replace('\'','').replace(' ','').strip('{}')
            numThreads = sum(self.types[th_type].values())
            if numThreads > 1:
                if len(self.types[th_type]) > 1:
                    print ' {}=[{}: {}]' .format(th_type, numThreads, states),
                else:
                    print ' {}=[{}]' .format(th_type, states),
            else:
                print ' {}=[{}]' .format(th_type,  self.types[th_type].keys()[0]),
                
        print "\n"

    def printThreads(self, states=[], types=[]):
        self.numPrinted = 0
        for tInfo in self.threads.values():
            if len(states) > 0 and tInfo.state not in states: continue
            if len(types) > 0 and len(tInfo.type) >0 and tInfo.type not in types: continue
            thread_summary = tInfo.summary()
            if self.pattern and not self.pattern.search(thread_summary): continue
            self.numPrinted += 1
            print '{} : {}'.format(self.numPrinted, tInfo.summary(self.bt_size))
            print



#############################################################################
#   Main
#############################################################################

def transform_cmline_arg(arg, options):
    # check if this is a negation
    negate = arg.find('~') >= 0

    # replace / with , and split
    given = set(arg.replace('/',',').replace('~','').replace(' ','').split(','))
    arg = set()
    if 'all' in given or '*' in given or negate: arg.update(options)
    given.discard('all')
    given.discard('*')

    #substring match
    for item in list(given):
        given.discard(item)
        given.update([o for o in options if o.find(item) >= 0])

    # remove negated items from all set
    if negate:
        for item in given:
            arg.discard(item)
    else:
        arg.update(given)

    return list(arg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Print mc/ep-engine thread information')
    parser.add_argument('--no-summary', dest='summary', default = True, action='store_false')

    parser.add_argument('-s', '--state', dest='state', type=str, default='active,lock', help = 'show */wait/lock/active threads')
    parser.add_argument('-t', '--type',  dest='type', type=str, default='all', help = 'show */executor/event/main/stats/logger threads')
    parser.add_argument('-d', '--debug', default = False, action='store_true')
    parser.add_argument('-b', '--backtrace', dest='backtrace', type=int, default=0, help = 'length of backtrace to print')
    parser.add_argument('--threads',  dest='threads', type=str, default='all', help = 'specific threads to debug')
    parser.add_argument('-p', '--process', dest='process', type=str, default='memcached', help = 'name of the process to analyze')
    parser.add_argument('-m', '--match', dest='match', type=str, default=None, help = 'str to match against backtrace')

    args = parser.parse_args()

    args.state = transform_cmline_arg(args.state, ['wait','lock','active'])
    args.type  = transform_cmline_arg(args.type, ['audit','executor','event','main','stats','logger'])

    if args.debug:
        print args
        sys.exit(0)
    
    ta = ThreadAnalyzer(args.process, args.threads, args.match, args.backtrace)
    ta.process()
    if args.summary: ta.summary()
    ta.printThreads(args.state, args.type)
    if args.summary and ta.numPrinted > 0: ta.summary()
