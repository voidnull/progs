#!/usr/bin/env python

import random

class Counter:
    def __init__(self,limit,count):
        self.limit=limit
        self.count=count

    def __repr__(self):
        return "[limit:%4d, count:%3d]" % (self.limit,self.count)

class NthPercentile:
    """
    This creates a fixed counter list with values starting from 0 to max with 'inc' increments
    limit is an explicit variable to try out different distributions later .

    """
    
    def __init__(self,max=5000,inc=10):
        self.counters=[]
        self.MAX=max
        self.INC=inc
        # adding one for overflow
        for n in xrange(0,max+inc+1,inc):
            self.counters.append(Counter(n,0))

    def clear(self):
        for item in self.counters:
            item.count=0

    def add(self,latency):
        "Because of fixed increments from 0"
        m=latency/self.INC
        if m<len(self.counters):
            self.counters[m].count+=1
            #print "add: %d : %d : %d" % (latency,m,self.counters[m].limit)
        else:
            self.counters[-1].count+=1
            #print "ovr: %d : %d : %d" % (latency,m,self.counters[-1].limit)

    def addLinear(self,latency):
        """
        This can be useful , if have different ranges than fixed increments
        Can be bettered with a binary search - O(log(N))
        """
        for item in self.counters:
            #print "xxx: %d : %d" % (latency,item.limit)
            if latency <= item.limit:
                item.count+=1
                #print "add: %d : %d" % (latency,item.limit)
                return;

        # we reach here if the latency is higher than the max set .
        # in this case let us just put it in the last one.
        self.counters[-1].count+=1
        #print "---: %d : %d" % (latency,self.counters[-1].limit)

    def getStats(self):
        total=0
        for item in self.counters:
            total+=item.count

        runningTotal=0
        jump=10
        n=1
        slab=total/jump
        print "Total Count : %d" %(total)

        lastvalidlimit=0
        for item in self.counters:
            runningTotal+=item.count
            if item.limit>0:
                lastvalidlimit=item.limit
            if runningTotal>=n*slab:
                print "%3d %% - %5d" % (n*jump,item.limit) 
                n+=1
        if n*jump<100:
            print "%3d %% - %5.2f" % (100,lastvalidlimit)

    def test(self,num=1000,maxlatency=5000):
        "Generate random latencys with num[total numbers to generate], maxlatency[maxlatency]"
        self.clear()
        
        print "Generating %d latencies within %d" % (num,maxlatency)
        for n in xrange(0,num):
            self.add(random.randint(0,maxlatency))

        self.getStats()
    

'''
*************** Main Module *********************
'''
if __name__ == '__main__':

    nth=NthPercentile()
    nth.test()
    
