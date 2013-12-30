#################################################################################
# - Implement a simple Elevator bank
# - N elevators , M floors (1-M)
# Usage:
#    Instantiate ElevatorController with N elevators and M floors
#    call an elevator to a floor.
# The current state will be printed out to elevator.state [tail -f ]
#################################################################################

import threading
import time
import logging
import random

class Direction:
    NONE = 0
    UP = 1
    DOWN = 2

    @staticmethod
    def state(d):
        if d==Direction.UP:
            return 'UP'
        elif d==Direction.DOWN:
            return 'DN'
        else:
            return 'ST'
    
class Elevator(threading.Thread):
    
    def __init__(self,id,numFloors=10):
        threading.Thread.__init__(self,name='elevator-'+str(id))
        self.id=id
        self.currentFloor=0
        self.numFloors=numFloors
        self.delay=0.25
        self.floorstates=[]
        for n in range(0,numFloors):
            self.floorstates.append(False)

        self.direction=Direction.NONE
        self.stopped=False
        
        self.lock=threading.RLock()
        self.cv=threading.Condition(self.lock)

    def goto(self,floor):
        "User clicks inside to goto a floor"
        floor= floor-1
        if floor<0 or floor>=self.numFloors:
            return

        self.cv.acquire()

        self.floorstates[floor]=True
        if self.direction == Direction.NONE:
            if floor<self.currentFloor:
                self.direction= Direction.DOWN
            elif floor>self.currentFloor:
                self.direction=Direction.UP

        self.cv.notify()
        self.cv.release()

    def cancel(self):
        "Clear all calls and stop the elevator"
        self.cv.acquire()
        self.stopped=True
        for n in range(0,numFloors):
            self.floorstates[n]=False
        self.cv.notify()
        self.cv.release()

    def ping(self):
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()

    def stop(self):
        "stop the elevator at the next floor"
        self.cv.acquire()
        self.stopped=True
        self.cv.notify()
        self.cv.release()

    def run(self):

        while not self.stopped:
            self.cv.acquire()

            while None==self.__getNextFloor() and not self.stopped:
                self.cv.wait()
                
            if self.stopped:
                self.cv.release()
                break;

            self.cv.notify()
            self.cv.release()
    
            n= self.__getNextFloor()

            if n!=None :
                self.__moveOneFloor()
            #print self

    def first(self):
        for n in range(0,self.numFloors):
            if self.floorstates[n]:
                return n
        return self.currentFloor

    def last(self):
        for n in range(self.numFloors-1,-1,-1):
            if self.floorstates[n]:
                return n
        return self.currentFloor


    def __getNextFloor(self):        
        if self.direction==Direction.NONE:
            # if the elev is stopped, check if there are any other floors
            # that it needs to go to
            for n in range(0,self.numFloors):
                if self.floorstates[n] and n!=self.currentFloor:
                    return n
            return None

        if self.direction==Direction.UP:
            for n in range(self.currentFloor,self.numFloors):
                if self.floorstates[n]:
                    return n
        elif self.direction==Direction.DOWN:
            for n in range(self.currentFloor-1,-1,-1):
                if self.floorstates[n]:
                    return n

        # no floor found
        self.direction=Direction.NONE
        return None

    def __moveOneFloor(self):
        if self.direction==Direction.NONE:
            f=None;
            for n in range(0,self.numFloors):
                if self.floorstates[n] and n!= self.currentFloor:
                   f=n
                   break
            if f==None:
                logging.error('no direction set')
                return False
            else:
                self.direction=Direction.DOWN if f<self.currentFloor else Direction.UP

        if self.direction==Direction.DOWN:
            nextFloor=self.currentFloor-1
        else:
            nextFloor=self.currentFloor+1

        if nextFloor<0 or nextFloor>=self.numFloors:
            logging.error('invalid next floor : %d' %(nextFloor))
            return False

        self.floorstates[self.currentFloor]=False
        time.sleep(self.delay)  
        self.currentFloor=nextFloor
        if self.floorstates[self.currentFloor]:
            time.sleep(self.delay*4)
        self.floorstates[self.currentFloor]=False
        return True

    def __repr__(self):
        s=""
        for n in range(0,self.numFloors):
            p=' '
            if n==self.currentFloor:
                p='*'
            elif self.floorstates[n]:
                p='+'

            s+= "%d%s " % ( n+1, p)

        return "[%s]:%s: %s" % (self.getName(),Direction.state(self.direction),s)



class ElevatorController(threading.Thread):

    def __init__(self,numElevators=1,numFloors=10):
        threading.Thread.__init__(self,name='controller');
        self.elevators=[]
        self.statefile='elevators.state'
        self.stopOtherElevators()
        for n in range(0,numElevators):
            e=Elevator(n+1,numFloors)
            self.elevators.append(e)
            e.start()
        self.numFloors = numFloors
        self.stopped =False
        self.start()

    def stopOtherElevators(self):
        "Stop other elevators - This is a helper method to stop other instances running via ipython "
        for t in threading.enumerate():
            if t.getName().startswith('elevator-') and t not in self.elevators:
                t.stop()
            elif t.getName().startswith('controller') and t != self:
                t.stopped=True

    def stop(self):
        "Stop the controller and elevators"
        for e in self.elevators:
            e.stop()

        self.stopped=True

    def run(self):
        "Currently just print stats to a file"
        n=0
        while not self.stopped :
            if self.statefile!=None:
                f=open(self.statefile,'w')
                f.write(self.state())
                f.close()
            if n%4==0:
                # Just to check for left out signals
                for e in self.elevators:
                    e.ping()
                
            time.sleep(0.25)
            
    def call(self,floor):
        floor=floor-1

        numStops = lambda(e,f,t): sum(e.floorstate[f:t])
        
        #calculate the minimum distance
        d=2*self.numFloors
        e=None
        for elev in self.elevators:
            new_d=abs(elev.currentFloor-floor)
            if floor<elev.currentFloor and elev.direction==Direction.UP:
                new_d += 2*abs(elev.currentFloor-elev.last())
            elif floor > elev.currentFloor and elev.direction==Direction.DOWN:
                new_d += 2*abs(elev.currentFloor-elev.first())
            #print "%s - d=%d - min=%d " % (elev.getName(),d,min_d)
            if new_d<d:
                d=new_d
                e=elev

        e.goto(floor+1)
        logging.warn("assigning [%s] to floor [%d]" % (e.getName(),floor+1))

    def state(self):
        l=["--controller--"]
        for e in self.elevators:
            l.append(str(e))

        return "\n".join(l)

    def simulate(self,num=20):
        for n in range(0,num):
            self.call(random.randint(1,self.numFloors+1))
            time.sleep(0.2)

    def __repr__(self):
        return self.state()
