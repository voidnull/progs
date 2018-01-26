#!/usr/bin/env python
import random
import sys
import string
import prefixtrie

'''
Collection of algorithms and puzzles
'''

class WordSplitter:
    '''
    split a word without spaces into a meaningful sentence
    eg: icanbesplit = i can be split
    '''
    def __init__(self):
        self.dictionary = prefixtrie.PrefixTrie()
        self.dictionary.loadFile('dict.txt')

    def split(self, oneword, words=[]):
        '''
        returns true or false
        has a list of tuples of start and end pos of each word
        '''

        start = 0
        if len(words) > 0 : start = words[-1][1] + 1
        if start >= len(oneword) : return True

        for n in range(start, len(oneword)):
            curword= oneword[start:n+1]
            found, isword = self.dictionary.check(curword)
            #print 'found:{},isword:{} : {}'.format(found,isword,curword)
            if isword:
                # word has been found
                words.append((start,n))
                remaining = self.split(oneword, words)
                if remaining: return True
                # not found
                words.pop()
            elif not found:
                # no words starting with curword
                return False

        return False

    def splitIntoWords(self, oneword):
        words = []
        if self.split(oneword,words):
            for w in words:
                print oneword[w[0]:w[1]+1],' ',
            print
        else:
            print 'word [{}] could not be split'.format(oneword)
        

class FindUnique:

    @staticmethod
    def run(arr=None):
        '''
        given an array of numbers where all numbers are repeated consecutively except one, find that one
        eg arr= [5,5,1,1,3,4,4] -> 3
        '''

        if arr == None:
            #generate the array
            nums=random.sample(range(1,100),random.randint(3,10))
            unique = random.choice(nums)
            arr = [x for n in nums for x in (lambda(y): [y] if y==unique else [y,y])(n)]
            print unique, arr

        l = 0
        r = len(arr)-1

        while l <= r :
            m = (r+l)/2
            #print 'in:',l,r,m
            if (m-l+1)%2 == 0:
                #even length
                if m>0 and arr[m] == arr[m-1]:
                    l=m+1
                elif m<r and arr[m] == arr[m+1]:
                    r=m-1
                else: return arr[m]
            else:
                if m>0 and arr[m] == arr[m-1]:
                    r = m - 2
                elif m<r and arr[m] == arr[m+1]:
                    l = m + 2
                else: return arr[m]
            #print 'out:',l,r,m

        #print 'final:',l,r,m
        return -1

    @staticmethod
    def test():
        numPassed = 0
        numFailed = 0
        for n in range(0,100):
            #generate the array
            nums=random.sample(range(1,100),random.randint(3,10))
            unique = random.choice(nums)
            arr = [x for n in nums for x in (lambda(y): [y] if y==unique else [y,y])(n)]
            #print unique, arr

            retVal = FindUnique.run(arr)
            if retVal != unique:
                print 'FAILED: retval={}, arr={}, unique={}'.format(retVal, arr,unique)
                numFailed += 1
            else:
                numPassed += 1

        print 'fail={} pass={}'.format(numFailed,numPassed)
            


def findSumSplitter(arr=None):
    '''
    split the given array into two parts of equal sum
    '''
    if arr == None:
        #generate the array
        arr=random.sample(range(1,100),random.randint(3,10))
    
    print len(arr),arr

    totalsum=sum(arr)
    cursum=0
    for n in range(0,len(arr)):
        if cursum*2 + arr[n] == totalsum:
            print '{} + [{}] + {} = {}'.format(arr[0:n],arr[n],arr[n+1:],totalsum)
            return
        cursum += arr[n]

def jumpingNumbers(N=100):
    '''
    A number is called as a Jumping Number if all adjacent digits in it differ by 1.
    The difference between 9 and 0 is not considered as 1.
    '''

    q = []
    for n in range(1,min(10,N)):
        q.append(n)
    print q
    while len(q)>0:
        num = q.pop(0)
        if num > N: continue; 
        print num, ' ',
        
        lastdigit = num % 10

        if lastdigit == 0:
            q.append(num*10+1)
        elif lastdigit == 9:
            q.append(num*10+8)
        else:
            q.append(num*10+(lastdigit-1))
            q.append(num*10+(lastdigit+1))

def subarraySum(arr=None, subsum=None):
    if arr == None:
        arr=random.sample(range(1,100),random.randint(3,10))

    if subsum == None:
        if random.randint(0,1) == 0:
            s=random.randint(0,len(arr)-1)
            e=random.randint(s,len(arr)-1)
            subsum = sum(arr[s:e+1])
        else:
            subsum = sum(arr)
            subsum = random.randint(subsum/5,subsum/2)

    s = 0
    e = 0
    cursum = arr[s]

    print subsum,':',arr
    
    while e < len(arr):
        print s,e,cursum,subsum
        if cursum < subsum:
            e+=1
            if e < len(arr) : cursum += arr[e]
        elif cursum > subsum:
            cursum -= arr[s]
            s+=1
        else:
            print s,e,cursum,subsum
            break;

    if cursum == subsum and s<=e:
        print 'subarray found:',s,e, arr[s:e+1]
    else:
        print 'no subarray found'


class LongestValidParen:

    @staticmethod
    def generate(size=20):
        return ''.join([random.choice('()') for c in range(0,random.randint(6,size))])
    
    @staticmethod
    def run(paren=None):
        if paren == None:
            paren=LongestValidParen.generate()

        stack = []
        maxlength = 0
        start = -1
        for i in range(0,len(paren)):
            c = paren[i]

            if c == '(':
                stack.append(i)
            else:
                if len(stack) == 0: continue
                val = stack.pop()
                if i-val+1 > maxlength:
                    maxlength = i-val+1
                    start = val

        print paren
        if maxlength>0:
            print '[{}@{}] = {}-{}-{}'.format(maxlength,start,paren[0:start],paren[start:start+maxlength],paren[start+maxlength:])
        else:
            print 'no valid set'


class Roman:

    @staticmethod
    def run(num):
        ROMAN=[
            (1000,'M'),
            (900,'CM'),
            (500,'D'),
            (400,'CD'),
            (100,'C'),
            (90,'XC'),
            (50,'L'),
            (40,'XL'),
            (10,'X'),
            (9,'IX'),
            (5,'V'),
            (4,'IV'),
            (1,'I')
            ]

        CHARMAP=dict([(b,a) for a,b in ROMAN])

        if type(num) == type(0):
            s=''
            for t in ROMAN:
                if num == 0: break
                n = num/t[0]
                if n > 0:
                    s = s + t[1]*n
                    num = num % t[0]
            
            return s
        else:
            s=num
            n=0
            num=0
            while n < len(s):
                if s[n:n+2] in CHARMAP.keys():
                    num += CHARMAP[s[n:n+2]]
                    n+=2
                elif s[n] in CHARMAP.keys():
                    num += CHARMAP[s[n]]
                    n+=1
                else:
                    n+=1
            return num

def pascal(N):
    prev = [0] * (N-1)
    curr = [0] * (N-1)

    for line in range(1,N):
        print line,':',
        for i in range(line):            
            if i == 0 or i == line-1:
                curr[i] = 1
            else:
                curr[i] = prev[i] + prev[i-1]
            print '{} '.format(curr[i]),
        prev,curr = curr,prev
        
        print
        

def pascalRecursive(n, k):
    '''
    f(n,k) = f(n-1,k) + f(n-1,k-1)
    f(0,0) = 1
    '''
    if n == k or k == 1:
        return 1

    return pascalRecursive(n-1,k) + pascalRecursive(n-1,k-1)

def groupNumbers():
    '''
    group numbers 0,1,2 together
    '''

    arr = [random.choice([0,1,2]) for n in range(random.randint(10,30))]

    def count(n):
        c=0
        for a in arr:
            if a==n: c+=1
        return c
    
    zeros=0
    twos=len(arr) - 1
    c1=(count(0),count(1),count(2))
    print arr,len(arr)
    n = 0
    run = 0
    while n <= twos:
        run += 1
        if arr[n] == 2 and n <= twos:
            arr[n] = arr[twos]
            arr[twos] = 2
        if arr[n] == 0 and n >= zeros:
            arr[n] = arr[zeros]
            arr[zeros] = 0

        while arr[twos] == 2: twos -= 1
        while arr[zeros] == 0 : zeros += 1
        if n < zeros:
            n = zeros
        else:
            n += 1
    c2=(count(0),count(1),count(2))
    check = 1
    for n in range(1,len(arr)):
        if arr[n] >= arr[n-1]: check +=1
    print arr,run,(c1 == c1 and check == len(arr))

def phonealpha(num):
    '''
    convert number to alpha..
    '''
    alphamap = ['0', '1', 'abc', 'def', 'ghi', 'jkl', 'mno', 'pqrs', 'tuv', 'wxyz']
    strnum = str(num)

    answer = ['']
    
    for digit in strnum:
        digit = int(digit)
        alphas = alphamap[digit]
        origsize = len(answer)
        for a in alphas:
            for n in range(origsize):
                answer.append(answer[n] + a)
        del answer[:origsize]

    return answer


def partition(arr,lo = 0,hi = -1):

    if hi == -1: hi = len(arr) - 1
    
    l = lo+1
    r = hi

    while True :
        while l < hi and arr[l] < arr[lo]: l += 1
        while r > lo and arr[r] > arr[lo]: r -= 1
        if l >= r: break
        arr[l], arr[r] = arr[r], arr[l]

    arr[r], arr[lo] = arr[lo], arr[r]
    return r

def kthlargest(arr, k):
    arr=list(arr)
    lo = 0
    hi = len(arr)-1

    while True:
        p = partition(arr,lo,hi)
        if p < k:
            lo = p+1
        elif p > k:
            hi = p -1
        else:
            return arr[k]

def qsort(arr,lo = 0 , hi = -1000):
    if hi == -1000 : hi = len(arr) - 1

    if lo < hi:
        p = partition(arr,lo,hi)
        qsort(arr,lo,p-1)
        qsort(arr,p+1,hi)
    

def validparen(s):
    '''
    remove invalid parenthesis and retun possible valid ones
    '''
    def flip(c):
        return '(' if c == ')' else ')'
    
    def flipstr(s):
        return ''.join([flip(c) for c in s])
    
    def validparen_inner(s,validset,lastinvalid,lastremoved,op='(',cp=')'):
        count = 0
        #if lastinvalid >= len(s):

        print s, lastinvalid, lastremoved
        for i in range(lastinvalid, len(s)):
            if s[i] == op: count += 1
            if s[i] == cp: count -= 1
            if count >=0: continue #valid

            # now we have invalid cp
            for j in range(lastremoved, i+1):
                #find the first cp and remove it
                if s[j] == cp and (j==lastremoved or s[j-1] != cp):
                    validparen_inner(s[:i]+s[i+1:] ,validset,i,j,op,cp)
            return
        validset.add(s)
    validset = set()
    validparen_inner(s,validset,0,0)
    rset = set()
    validparen_inner(s[::-1],rset,0,0,')','(')
    validset.update([k for k in rset])
    return validset
    

def toEnglish(num):
    if num == 0 : return "zero"

    triples_names = ['Thousand','Million','Billion','Trillion']
    tens_names    = ['','Ten','Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    elevens_names = ['Ten','Eleven','Twelve','Thirteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    ones_names    = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine']

    def under1000(n):
        o = n % 10
        t = (n/10) % 10
        h = n/100

        english = []
        
        if o > 0 and t!=1:
            english.append(ones_names[o])
        elif t == 1:
            english.append(elevens_names[o])

        if t > 1:
            english.append(tens_names[t])

        if h > 0:
            english.append('Hundred')
            english.append(ones_names[h])

        return english

    human = []
    n = 0
    while num > 0 :
        human.extend(under1000(num%1000))
        num /= 1000
        if num %1000 != 0:
            human.append(triples_names[n])
        n += 1
        
    human.reverse()
    return human

def minwindow(hay,needle):
    '''
    find the smallest substring in hay that
    contains all chars in needle
    '''

    charmap = {}
    count = len(needle)
    begin =0
    end = 0
    start = 0
    dist=sys.maxint
    # count the chars in needle
    for c in needle:
        charmap[c] = charmap.get(c,0)+1
    #print charmap
    while end < len(hay):
        c = hay[end]
        end +=1
        if c in charmap:
            if charmap[c] > 0 :
                count -= 1
                charmap[c] -= 1
        #print count,begin,end,start,dist,charmap
        while count == 0:
            if end-begin < dist :
                dist = end-begin
                start= begin
            c = hay[begin]
            if c in charmap:
                if charmap[c] == 0:
                    count += 1
                    charmap[c] +=1 
            begin += 1

    return hay[start:start+dist] if dist != sys.maxint else ''

def maxwindow(hay,needle):
    '''
    find the smallest substring in hay that
    contains all chars in needle
    '''

    charmap = {}
    count = len(needle)
    begin =0
    end = 0
    start = 0
    dist=0
    # count the chars in needle
    for c in needle:
        charmap[c] = charmap.get(c,0)+1
    print charmap
    while end < len(hay):
        c = hay[end]
        end +=1
        if c in charmap:
            if charmap[c] == 0 :
                count += 1
                charmap[c] += 1
        print count,begin,end,start,dist,charmap
        while count > 0:
            print count,begin,end,start,dist,charmap
            c = hay[begin]
            begin += 1
            if c in charmap:
                if charmap[c] > 1:
                    count -= 1
                    charmap[c] -=1 
            
            if end-begin > dist :
                dist = end-begin
                start= begin


    return hay[start:start+dist] if dist != 0 else ''

def reconstructQueue(people):
    print people
    people.sort(key=lambda (h, k): (-h, k))
    print people
    queue = []
    for p in people:
        queue.insert(p[1], p)
        print queue
    return queue
        

def genCombinations(s="abcd"):

    def combos(s,pos,combo,vecCombo):
        if pos == len(s):
            vecCombo.append(''.join(combo))
            return

        combos(s,pos+1,combo,vecCombo)
        combo.append(s[pos])
        combos(s,pos+1,combo,vecCombo)
        combo.pop()

    vec=[]
    combos(s,0,[],vec)
    return vec

def genPermutations(s='abcd'):

    def perms(s, vecPerms, curPerm=[], table=set()):
        print curPerm, table
        if len(curPerm) == len(s):
            vecPerms.append(''.join(curPerm))
            return
        for n in range(0,len(s)):
            if n not in table:
                curPerm.append(s[n])
                table.add(n)
                perms(s, vecPerms, curPerm,table)
                table.remove(n)
                curPerm.pop()

    vecPerms=[]
    perms(s, vecPerms)
    return vecPerms
    

def wordLadder(word='ape',final=None):
    d=set()
    with open("dict.txt") as f:
        for line in f:
            d.add(line.strip())

    q = []
    wordpos = []
    q.append(word)
    wordpos.append(-1)
    nomore=set()
    while len(q) > 0 and len(q) < 20 and (final == None or final != q[-1]):
        print q
        top = q[-1]
        pos  = wordpos[-1]
        added = False
        for n in range(len(top)):
            if n == pos : continue
            lword = list(top)
            for c in string.ascii_lowercase:
                lword[n] = c
                word = ''.join(lword)
                if word not in q and word not in nomore and word in d:
                    #print word,n,top
                    q.append(word)
                    wordpos.append(n)
                    added = True
                    break;
            if added:break;

        if not added:
            nomore.add(q.pop())
            wordpos.pop()

    print q


def countbits(n) :
    def bits(n):
        c = 0
        while n > 0:
            c += 1
            n &= (n-1)
        return c

    upto15 = []
    for i in range(16):
        upto15.append(bits(i))


    count = 0
    mask = 0xF
    while n > 0:
        count += upto15[n & mask]
        n >>=4

    return count
        
        
def countRangeSum(arr,l,u):

    def naive(arr,l,u):
        count = 0
        sums= list(arr)
        sums[0] = arr[0]
        for n in range(1,len(sums)):
            sums[n] = arr[n] + sums[n-1]

        for i in range(len(sums)-1):
            for j in range(i+1,len(sums)):
                s =  sums[j] - sums[i]
                if s >=l and s <= u:
                    count+=1
        return count

    def optimal(arr,l,u):
        s = 0
        e = 0
        total = arr[e]
        count = 0

        while e < len(arr) and count < 20:
            print s,e,total,count
            if total >= l and total <= u:
                count += 1

            if total <= l :
                e+=1
                total += arr[e]
            elif total >= u:
                total -= arr[s]
                s+=1

        if total >= l and total <= u:
            count += 1

        return count
        
    
    return optimal(arr,l,u)

def median(A=[1,3,5,7],B=[2,4,6,8]):

    A.sort()
    B.sort()
    if len(A) > len(B):
        A, B = B, A
    
    lenA, lenB = len(A), len(B)

    imin = 0
    imax = lenA
    half = (lenA + lenB + 1)/2
    j = 0
    med = 0
    
    while imin <= imax:
        i = (imin + imax) / 2
        j = half - i
        print 'i={} j={} imin={} imax={} lenA={} lenB={}'.format(i,j,imin,imax,lenA,lenB)
        
        if i > 0 and j < lenB  and A[i-1] > B[j]:
            # decrease i
            imax -= 1
        elif  j > 0 and i < lenA and B[j-1] > A[i]:
            imin += 1

        else:
            left = 0
            right = 0

            if i == 0: left = B[j-1]
            elif j == 0: left = A[i-1]
            else:
                left = max(A[i-1], B[j-1])

            if (lenA + lenB) % 2 == 1:
                med =  left
                break;

            if i >= lenA : right = B[j]
            elif j >= lenB : right = A[i]
            else:
                right = min(A[i],B[j])

            med = (left + right) / 2.0
            break

    C = []
    C.extend(A)
    C.extend(B)
    C.sort()

    print 'med={} -- A={} B={}'.format(med,A, B)
    lenC = len(C)
    med =  (C[lenC/2] + C[lenC/2 -1])/2.0 if lenC %2 ==0  else C[lenC/2]
    print 'med={} -- C={}'.format(med,C)
    
def rainwater(arr=[0,1,0,2,1,0,1,3,2,1,2,1]):
    leftmax = list(arr)
    rightmax = list(arr)

    for i in range(1,len(arr)):
        leftmax[i] = max(arr[i], leftmax[i-1])

    for i in range(len(arr)-2,-1,-1):
        rightmax[i] = max(arr[i], rightmax[i+1])

    ans = 0

    for i in range(0,len(arr)):
        ans += min(leftmax[i],rightmax[i]) - arr[i]
        print 'l={} r={} h={} w={} tot={}'.format(leftmax[i],rightmax[i],arr[i],(min(leftmax[i],rightmax[i]) - arr[i]),ans)

    return ans

def nsum(n,cursum=0,numlist=[]):
    '''
    print all combos of numbers summing up to N
    eg.N = 4
      1,1,1,1
      1,1,2
      2,2
      1,3
      4
    '''

    if 0 == n:
        print numlist
        return numlist

    fromnum = 1
    fromnum = 1 if len(numlist) == 0 else numlist[-1]
    for i in range(fromnum,n+1):
        
        #if len(numlist) > 0 and numlist[-1]<i: continue
        cursum += i
        numlist.append(i)
        nsum(n-i,cursum,numlist)
        cursum -= numlist.pop()

    return numlist

def spiral(N, M):
    '''
    fill a matrix in spiral order eg.
    1 2 3
    8 9 4
    7 6 5
    '''
    x,y = 0,0   
    dx, dy = 0, -1
    num = 0
    matrix=[[0] * N for i in range(M)]

    for dumb in xrange(N*M):
        if abs(x) == abs(y) and [dx,dy] != [1,0] or x>0 and y == 1-x:  
            dx, dy = -dy, dx            # corner, change direction

        if abs(x)>N/2 or abs(y)>M/2:    # non-square
            dx, dy = -dy, dx            # change direction
            x, y = -y+dx, x+dy          # jump

        matrix[x][y] = dumb
        x, y = x+dx, y+dy

    return matrix

