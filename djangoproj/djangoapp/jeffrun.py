from csc.conceptnet4.models import Concept
from csc.nl import get_nl
from csc.util.persist import get_picklecached_thing
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db

def xuniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc
                
from operator import itemgetter
def xcombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xcombinations(items[:i]+items[i+1:],n-1):
                yield [items[i]]+cc                

#note:  'haunt' and 'supernatural' and 'thriller' doesn't get any hits                
mywords = ['classical music', 'movie', 'golf', 'concentrate', 'thrill', 'mystery', 'death', 'ghost',  'mozart','music' , 'spirit', 'scary', 'evil', 'fanatic', 
           'spiritual path', 'trance', 'meditate', 'sex', 'actor']

#this makes all pairs of the list of words
mypairs = []
for uc in xcombinations(mywords,2): mypairs.append(uc)

features_exists = ['IsA', 'DefinedAs', 'SymbolOf', 'MadeOf', 'AtLocation', 'CreatedBy', 'LocatedNear', 'PartOf', 'HasPrerequisite',  'HasProperty', 'ConceptuallyRelatedTo']  
features_actions=['Causes', 'Desires', 'HasSubevent', 'HasFirstSubevent', 'HasLastSubevent', 'CausesDesire', 'CapableOf', 'InheritsFrom']
features_asobject = ['UsedFor', 'MotivatedByGoal', 'ObstructedBy', 'CreatedBy', 'ReceivesAction', 'ObstructedBy']
features_asemotional= [ 'Desires', 'MotivatedByGoal', 'CausesDesire']




out=[]
#do some first-order analysis on these words
out.append('*********most common assertions ************')

for w in mywords:
    try:
        concepts = Concept.get(w, 'en')
        out.append(w)
        for a in concepts.get_assertions()[:15]:
            out.append("     " + str(a))
        out.append('')     
    except:
        pass

#analyze relationships using a 2d analogy space
#absolute values
cnet = conceptnet_2d_from_db('en')
analogyspace = cnet.svd(k=100)
#normalized
cnet_norm = conceptnet_2d_from_db('en').normalized()
analogyspace2 = cnet_norm.svd(k=100)

out.append('*********associateive strength not normalized  ************')
out.append('(in other words, large numbers just represent greater strength')
out.append(' but do not pretend to measure anything else)')
out.append(' ')
for w in mywords:
    #get all dot products and pick best ones
    try:
        this_u_vector = analogyspace.weighted_u[w, :]
        this_like = analogyspace.u_dotproducts_with(this_u_vector)
        topItems = this_like.top_items()
        out.append('')
        out.append( 'the things most closely related to *%s* are' %w)
        for t in topItems:
            out.append( '     ' + str(t) )
    except:
        out.append('cnet_norm has no entries for %s' %w)

#test the word pairs
out.append(' ')
out.append(' ')
out.append('*********associateive strength normalized (scale -1.0 to 1.0 ) ************')
out.append(' ')
mypairs = []
for uc in xcombinations(mywords,2): mypairs.append(uc)
outarr=[];tmparr=[]; grouparr= [];lasttopic = mypairs[0][0];allarr=[]
out.append('')
for p in mypairs:
    a = None; b = None; a_versus_b = None; thistopic = p[0]
    aword=p[0]; bword = p[1]
    try:       
        a= analogyspace.weighted_u[aword,:]
    except:
        print "issue with the word %s" %aword
    try:
        b= analogyspace.weighted_u[bword,:]
    except:
        print "issue with the word %s" %bword
    try:
        a_versus_b = a.hat().dot(b.hat())
        #out.append('%s is related to %s:  %s' %(aword, bword, str(a_versus_b)))
        print '%s is related to %s:  %s' %(aword, bword, str(a_versus_b))
        allarr.append(["%s : %s" %(aword, bword), a_versus_b])
        
        if lasttopic == thistopic:
            tmparr.append(["%s : %s" %(aword, bword), a_versus_b])
        else:
            tmparr.sort(key=itemgetter(1, 0))
            for t in tmparr:
                grouparr.append(t)
            grouparr.append([])    
            tmparr = []
            lasttopic = thistopic
            
    except:
        print "couldn't find an association between %s and %s" %(aword, bword)
        
allarr.sort(key=itemgetter(1,0))
ix = 1
for a in allarr: #print every other line
    if ix%2 >0:
        out.append(a)
    ix+=1
out.append('')
out.append('')
        
tmparr.sort(key=itemgetter(1, 0))
for t in tmparr:
    grouparr.append(t)
    
out.append('')
out.append('')
for o in grouparr:
    out.append(o)    
    
outfile = open('associations.txt', 'w')

for q in out:
    if isinstance(q, list):
        for x in range(0, len(q)):
            outfile.write (str(q[x]) + "\t")
            if str(q[x]) =='meditate : ghost':
                pass
            
        outfile.write('\n')                   
    else:
        outfile.write(str(q) + '\n')

pass
    
  
