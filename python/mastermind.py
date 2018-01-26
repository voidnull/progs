import random
import itertools

class Hint:
    def __init__(self, s =0 ,w =0):
        self.strong = s
        self.weak = w

    def isWin(self,size=4):
        return self.strong == size

    def inInvalid(self):
        return self.strong == -1

    def __eq__(self, other):
        return self.strong == other.strong and self.weak == other.weak

    def __gt__(self, other):
        return self.strong > other.strong or self.weak > other.weak

    def __repr__(self):
        return '[hint = strong:{} weak:{}]'.format(self.strong,self.weak)

    def __str__(self):
        return '[strong:{} weak:{}]'.format(self.strong,self.weak)

#--------------------------------------------------------------------------------

class MasterMind:
    '''
    colors = a-f
    '''
    @staticmethod
    def get_hint(secret, guess):
        size = len(secret)
        if len(guess) != size:
            return Hint(-1,-1)
        
        hint = Hint()
        secret = list(secret)
        guess  = list(guess)
        for n in range(size):
            if guess[n] == secret[n]:
                hint.strong += 1
                secret[n] = '-'
                guess[n] = '-'
        for n in range(size):
            if guess[n] == '-' : continue
            for m in range(size):
                if guess[n] == secret[m]:
                    hint.weak +=1
                    secret[m] = '-'

        return hint
                    
    def __init__(self, chars='abcdef', size=4):
        self.SIZE = size
        self.CHARS = chars
        self.generate_secret()

    def generate_secret(self):
        self.secret = ''.join(random.sample(self.CHARS , self.SIZE))

    def eval_guess(self, guess):
        return self.get_hint(self.secret, guess)


    def auto_play(self):
        self.generate_secret()
        print 'secret: {}'.format(self.secret)
        hint = Hint()
        count = 1
        player = Player()
        guess = player.next_move(None,None)
        while count < 100:
            hint = self.eval_guess(guess)
            print '{} : {} : {} : [rem.possibities: {}]'.format(count,''.join(guess), hint, len(player.subset))
            if hint.isWin():
                print 'Game won'
                break
            guess = player.next_move(guess,hint)
            count += 1
            

#--------------------------------------------------------------------------------
    
class Player:

    def __init__(self, chars='abcdef', size=4):
        # all possibilities
        self.ALL = list(itertools.product(chars,repeat=size))
        self.CHARS = chars
        # this subset will have only the needed possibilities
        self.subset = list(self.ALL)
        self.SIZE = size
        self.moves = []

    def _my_next_move(self,move):
        self.moves.append(move)
        return move

    def first_move(self):
        #return self._my_next_move(self.CHARS[0] * (self.SIZE))
        # aabb
        return self._my_next_move(self.CHARS[0] * (self.SIZE/2) + self.CHARS[1] * (self.SIZE-(self.SIZE/2)))
    
    def next_move(self, prevMove = None, hint = None):
        if prevMove == None:
            # this is the first move
            return self.first_move()

        if hint.isWin():
            print "I've won !!!"
            return None

        # Remove from subset all the items that will NOT give the hint
        self.subset = [ x for x in self.subset if MasterMind.get_hint(x, prevMove) == hint]

        return self._my_next_move(random.choice(self.subset))
        
