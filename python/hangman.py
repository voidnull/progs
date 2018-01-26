#!/usr/bin/env python
import pprint
import random
import string

class HangMan:

    class GameState:
        def __init__(self,hangman):
            self.reset()
            self.hangman = hangman

        def reset(self):
            self.destWord = None
            self.numGuesses = 0
            self.matchedPos = set()
            self.matchedChars = set()
            self.missedChars = set()
            self.prevGuesses = set()
            self.wordset = set()
            self.lastGuess = ' '
            self.err = '*'
            
        def start(self) :
            self.reset()
            self.err = '*'
            self.destWord = random.choice(self.hangman.wordlist)

        def getValidPositions(self,c):
            'get the identified positions of the char'
            if c not in self.matchedChars: return []

            l = []
            for p in self.matchedPos:
                if self.destWord[p] == c:
                    l.append(p)

            return l

        def removeMatchingMissed(self):
            if len(self.wordset) == 0 or len(self.missedChars) == 0: return
            # remove all items from self.wordset that have this char
            remove=set()
            for wp in self.wordset:
                for c in self.hangman.wordlist[wp]:
                    if c in self.missedChars:
                        remove.add(wp)
                        break
            self.missedChars.clear()
            self.wordset.difference_update(remove)

        def updateWordset(self,c):
            d = self.hangman.d[self.getWordLength()]
            for p in self.getValidPositions(c):
                # get the words that have the guesschar in this pos
                #print guessChar, p 
                if len(self.wordset) == 0:
                    self.wordset.update(d[c][p])
                else:
                    self.wordset.intersection_update(d[c][p])
            self.removeMatchingMissed()

        def getWordLength(self):
            return 0 if self.destWord == None else len(self.destWord)

        def dump(self):
            guessWord = '-' * len(self.destWord)
            for n in range(len(self.destWord)):
                if n in self.matchedPos:
                    guessWord = guessWord[:n] + self.destWord[n] + guessWord[n+1:]

            print '{:<3} : {}  : {} : [{}/{}] : {} : [{}]'.format(self.numGuesses,
                                                                  self.lastGuess,
                                                                  guessWord,
                                                                  len(self.matchedPos),
                                                                  len(self.destWord),
                                                                  self.err,
                                                                  len(self.wordset))

        def isDone(self):
            return self.destWord != None and len(self.matchedPos) == len(self.destWord)

        def isStarted(self):
            return self.destWord != None

    
    def __init__(self, filename='dict.txt'):
        self.loadDictionary(filename)
        self.state = HangMan.GameState(self)
        
    def loadDictionary(self, filename):
        self.d = {}
        self.wordlist=[]
        f=open(filename)
        for line in f:
            word = line.strip().lower()
            self.wordlist.append(word)

        def cmp(x,y):
            if len(x) != len(y):
                return len(x) - len(y)
            if x == y : return 0
            if x < y  : return -1
            return 1
        
        self.wordlist.sort(cmp)
        self.processWords()

    def processWords(self):
        if len(self.d) > 0 : return
        for n in range(len(self.wordlist)):
            word = self.wordlist[n]
            l = len(word)
            self.d.setdefault(l,{})
            d = self.d[l]
            for pos in range(len(word)):
                c = word[pos]
                if c not in d : d[c] = {}
                if pos not in d[c]: d[c][pos] = []
                d[c][pos].append(n)
        
    def guess(self, c = None, state = None):
        if state == None:
            state = self.state
        state.err = ''
        state.lastGuess = c
        try:
            if not state.isStarted() or state.isDone():
                print '... Starting a New Game ...'
                state.start()
            
            if c == 'None': return False
            c = c.lower()
            if c in state.prevGuesses:
                state.err = '-' 
                return False
            
            state.numGuesses += 1
            state.prevGuesses.add(c)

            if c not in state.destWord:
                state.err = 'x'
                state.missedChars.add(c)
                return False

            state.matchedChars.add(c)
            for n in range(len(state.destWord)):
                if state.destWord[n] == c:
                    state.matchedPos.add(n)
            state.err = '+'
            
            if state.isDone():
                state.err = '='

            return True

        finally:
            state.dump()

    def autoPlay(self,word = None):
        state = HangMan.GameState(self)
        self.state = state
        state.start()
        if word != None:
            state.destWord = word
        state.dump()

        vowels = ['a','e','i','o','u']
        while not state.isDone():
            numMatched = len(state.matchedPos)
            guessChar = None
            if numMatched * 3 < state.getWordLength() and len(vowels) > 0:
                # try more vowels
                guessChar = random.choice(vowels)
                vowels.remove(guessChar)
            elif len(state.wordset) > 0:
                while guessChar == None:
                    word= self.wordlist[random.sample(state.wordset,1)[0]]
                    #print word
                    for c in word:
                        if c not in state.prevGuesses:
                            guessChar = c
                            break
            elif 'y' not in state.prevGuesses:
                guessChar='y'
            else:
                print 'picking random'
                guessChar = random.choice(string.ascii_lowercase)

            r = self.guess(guessChar,state)
            state.updateWordset(guessChar)
