
class Node:
    def __init__(self):
        self.complete=False
        self.children={}

    def __repr__(self):
        return self.children.__repr__()


class PrefixTrie:

    def __init__(self):
        self.root=Node()

    def add(self,word,transform=lambda x: x.lower()):
        if len(word)==0:
            return
        if transform:
            word=transform(word)
        node=self.root
        for c in word:
            if c not in node.children:
                node.children[c]=Node()
            node=node.children[c]

        node.complete=True

    def loadFile(self,filename,transform=lambda x: x.lower()):
        f=open(filename)
        for line in f:
            line=line.strip()
            self.add(line,transform)

    def check(self,word):
        found=False
        complete=False

        node=self.root
        for c in word:
            if c in node.children:
                node=node.children[c]
            else:
                return (found,complete)

        found=True
        complete=node.complete

        return (found,complete)


    def findLongestPrefix(self,node,cur=[]):
        lprefix=''
        numkids=len(node.children)
        if numkids>0:
            for c in node.children:
                cur.append(c);
                prefix = self.findLongestPrefix(node.children[c],cur)
                cur.pop()
                if prefix==None :
                    if numkids>=2:
                        if len(cur)>len(lprefix):
                            lprefix=''.join(cur)
                else:
                    if len(lprefix)<len(prefix):
                        lprefix=prefix
                        
            return lprefix
        else:
            #leaf..
            return None 
                
    def __repr__(self):
        return self.root.__repr__()
    
    
