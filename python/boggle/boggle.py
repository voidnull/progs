#!/usr/bin/env python
import prefixtrie
import pprint


"""
Given a Boggle board [http://en.wikipedia.org/wiki/Boggle] , this
class attempts to solve the board.
"""
class Char:
    def __init__(self,char='A'):
        self.char=char
        self.inuse=False

    def __str__(self):
        return self.char

    def __repr__(self):
        return "%s%s" % (self.char,'*' if self.inuse else ' ')

class BoggleSolver:

    def __init__(self,fileName='dict.txt'):
        self.board=[]
        self.reuse=True;
        self.trie=prefixtrie.PrefixTrie()
        if fileName !=None:
            self.trie.loadFile(fileName)

        self.initBoard('atgc,lrje,jrfg,mhes')
        #'sers,patg,line,sers'

    def initBoard(self,s=None):

        if s==None:
            size=len(self.board)
            for i in range(0,size):
                for j in range(0,size):
                    self.board[i][j].inuse=False
            return
            
        s=s.replace(' ','')
        rows=s.lower().split(',')
        self.board=[]

        for row in rows:
            l=[]
            for c in row:
                l.append(Char(c))
            self.board.append(l)


    def solve(self):
        size=len(self.board)
        self.points=0
        self.count=0
        for i in range(0,size):
            for j in range(0,size):
                #print "Starting search [%d:%d]" % (i,j)
                self.findWords(i,j,[])

        print "Count=%d Points=%d" % (self.count,self.points)


    def __wordFound(self,word):
        #print word
        self.count += 1
        lenw=len(word)
            
        if lenw == 3 or lenw==4:
            self.points+=1 
        elif lenw==5:
            self.points+=2
        elif lenw==6:
            self.points+=3
        elif lenw==7:
            self.points+=5
        elif lenw>=8:
            self.points+=11
            

    def findWords(self,r,c,l):
        
        if r < 0 or r>=len(self.board):
            return False;
        if c < 0 or c>=len(self.board):
            return False;

        if self.board[r][c].inuse :
            return False

        l.append(self.board[r][c].char)

        (found,complete) = self.trie.check(l)
        #print "[%d:%d - %s : %s,%s]" % (r,c,''.join(l),found,complete)

        if complete:
            self.__wordFound(''.join(l))
            

        self.board[r][c].inuse=True

        if found:
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if not (i == 0 and j==0):
                        complete =  self.findWords(r+i,c+j,l) or complete

        self.board[r][c].inuse=False
        
        l.pop();
        return complete

    def hasWord(self,word):
        size=len(self.board)        
        for i in range(0,size):
            for j in range(0,size):
                #print "Starting search [%d:%d]" % (i,j)
                if self.hasWordInPos(word,0,i,j):
                    return True
        return False

    def hasWordInPos(self,l,pos,r,c):
        
        if r < 0 or r>=len(self.board):
            return False;
        if c < 0 or c>=len(self.board):
            return False;

        if pos>=len(l):
            return False

        #print "(%d:%d-[%s:%s]-%d,%s)" % (r,c,self.board[r][c].char,self.board[r][c].inuse,pos,l[pos])

        if self.board[r][c].inuse :
            return False

        if self.board[r][c].char != l[pos]:
            return False
        
        self.board[r][c].inuse=True

        if pos == len(l)-1 :
            # The word has been found
            pprint.pprint(self.board)
            found=True
        else:
            found = False
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if not (i == 0 and j==0) and not found :
                        found =  self.hasWordInPos(l,pos+1,r+i,c+j)
                        if found:
                            break;

        self.board[r][c].inuse=False
        return found

            

            
    
