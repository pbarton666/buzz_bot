import string
import model

class Translator(object):
    #this from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303342  
    #very handy string parser  called thus:  clean = Translator(keep = string.ascii_lowercase)
    allchars = string.maketrans('','')
    def __init__(self, frm='', to='', delete='', keep=None):
        if len(to) == 1:
            to = to * len(frm)
        self.trans = string.maketrans(frm, to)
        if keep is None:
            self.delete = delete
        else:
            self.delete = self.allchars.translate(self.allchars, keep.translate(self.allchars, delete))
    def __call__(self, s):
        return s.translate(self.trans, self.delete)  


class Analyzer(object):
    cleaner = Translator(keep=string.ascii_lowercase + " \n\t")

    def __init__(self):
        self.NEGATIVE = set(w.word for w in model.NegWords.select())
        self.POSITIVE = set(w.word for w in model.PosWords.select())
        self.OBSCENE = set(w.word for w in model.ObsceneWords.select())

    def analyze(self, content):
    
        #conduct an analysis on a single block of relevant content.  This will obviously get more sophisticated, but for now
        #  we'll look for positive and negative associations of each surrounding word using Harvard's semantic dictionary
    
        #Instantiate a translator object and tell it what to keep (we'll get rid of punctuation)
        tran = Translator(keep=string.ascii_lowercase)

        word_distribution = {}
        for word in cleaner(content.tolower()).split():
            if len(word) < 4:
                continue
            word_distribution[word].setdefault(0)
            word_distribution[word] += 1

        poswords, negwords, obscenewords = 0, 0, 0

        for word, count in word_distribution.iteritems()
            if word in self.NEGATIVE:
                negwords += count
            elif word in self.POSITIVE:
                poswords += count
            elif word in self.OBSCENE:
                obscenewords += count
        
        return poswords - negwords - obscenewords
        
        

    def analyzeContent(self, product,search):
    
        #conduct an analysis on each block of relevant content.  This will obviously get more sophisticated, but for now
        #  we'll look for positive and negative associations of each surrounding word using Harvard's semantic dictionary
    
        model.Word.deleteBy(searchid = search)
        #Instantiate a translator object and tell it what to keep (we'll get rid of punctuation)
        tran= Translator(keep = string.ascii_lowercase)
    
        #load content table
        mycont = model.Content.selectBy(searchid=search)
        contentIx = 0
        wordIx = 0
        for c in mycont: 
            contID = c.id
            urlID = c.urlid
            content= c.cont
            date= c.dateaccessed
            #look thru the words
            mywords = content.split()
            poswords = 0
            negwords=0
            obscenewords = 0
            for w in mywords: 
                #disregard really short words and those w/ & (likely html constants)
                if len(w) > 3 and w.find('&')<0:
                    w = w.lower()
                    w = tran(w)
                    polarity = ""
                    #find out what the dictionary has to say about the word
                    neghits = model.NegWords.selectBy(word  = w).count()
                    if neghits > 0: negwords = negwords+1
                    poshits = model.PosWords.selectBy(word  = w).count()
                    if poshits > 0: poswords = poswords+1
                    obscenehits = model.ObsceneWords.selectBy(word  = w).count()
                    if obscenehits > 0: obscenewords = obscenewords+1
                    if neghits+obscenehits >0: polarity = 'negative'
                    if poshits>0: polarity = 'positive'
                    if len(polarity)>0:
                        model.Word(word = w, connotation = polarity, urlid = urlID,
                                   contid = contID)
            polarityscore = poswords - negwords - obscenewords            
            rowObj = model.Content.get(c.id)
            rowObj.set(polarity=polarityscore)
    
