from csc.conceptnet4.models import Concept
from csc.nl import get_nl
from csc.util.persist import get_picklecached_thing
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db
from cnet_utilities import xuniqueCombinations as xuniqueCombinations
from cnet_utilities import xcombinations as xcombinations
from operator import itemgetter

#note:  'haunt' and 'supernatural' and 'thriller' doesn't get any hits                
mywords = [ 'movie', 'music' , 'actor']

#this makes all pairs of the list of words
mypairs = []
for uc in xcombinations(mywords,2): mypairs.append(uc)

features_exists = ['IsA', 'DefinedAs', 'SymbolOf', 'MadeOf', 'AtLocation', 'CreatedBy', 'LocatedNear', 'PartOf', 'HasPrerequisite',  'HasProperty', 'ConceptuallyRelatedTo']  
features_actions=['Causes', 'Desires', 'HasSubevent', 'HasFirstSubevent', 'HasLastSubevent', 'CausesDesire', 'CapableOf', 'InheritsFrom']
features_asobject = ['UsedFor', 'MotivatedByGoal', 'ObstructedBy', 'CreatedBy', 'ReceivesAction', 'ObstructedBy']
features_asemotional= [ 'Desires', 'MotivatedByGoal', 'CausesDesire']

out=[]
#do some first-order analysis on these words
out.append('*********these are the most common relationships ascribed to the key words************')

for w in mywords:
    try:
        concepts = Concept.get(w, 'en')
        out.append(w)
        for a in concepts.get_assertions()[:20]:
            out.append("     " + str(a))
        out.append('')     
    except:
        pass

'''Create a pca based on the normalized relationships between every item on the list
   and every other item known to the database (row-wise normalization).  This produces a scale-
   free assay of how similar other things are.  In other words, we ask what concepts are most
   similar to each of our key words.  The max is 1.0.
   '''
pca_axes = 20  #this is the number of axes we'll extimate
cnet = conceptnet_2d_from_db('en')   #this is the database we're drawing from 
cnet_norm = conceptnet_2d_from_db('en').normalized()   #this normalizes the data
analogyspace = cnet_norm.svd(k=pca_axes)   #this conducts the pca on the normalized data

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

#we'll write a copy of our output for posterity
outfile_name = "associations.txt"
outfile = open('outfile_name.txt', 'w')

for q in out:
    if isinstance(q, list):
        for x in range(0, len(q)):
            outfile.write (str(q[x]) + "\t")
            
        outfile.write('\n')                   
    else:
        outfile.write(str(q) + '\n')

pass
    
  
