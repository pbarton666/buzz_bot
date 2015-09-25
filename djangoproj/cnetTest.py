
from csc.conceptnet4.models import Concept
from csc.nl import get_nl


#...tap the database to explore some concept
dog = Concept.get('dog', 'en')
print ''
print "here are the key associations with %s" %'dog'
for fwd in dog.get_assertions_forward()[:20]:
    print fwd
print ''    

#this does a pca on a pickled tensor and finds things related to a word
from csc.util.persist import get_picklecached_thing
tensor = get_picklecached_thing('tensor.gz')
#runs the svd
svd = tensor.svd(k=100)


#find similar  concepts to a word
myword = 'teach'
print myword
most_associated = svd.u_dotproducts_with(svd.weighted_u_vec(myword)).top_items(10)
print ''
print 'these words are most associated with %s' %myword
for m in most_associated:
    print m
	
	
#predict properties of a word
props = svd.v_dotproducts_with(svd.weighted_u_vec(myword)).top_items(10)
print ''
print 'these are the properties we most associate with %s' %myword
for p in props:
    print p
		
#these evaluate some assertions
#is a dog a pet?
metric = svd.get_ahat(('dog', ('right', 'IsA', 'pet')))
print ''
print 'here is a measure of the likelihood that a %s is a %s (high numbers show likelihood): %s' %('dog', 'pet', str(metric))

# ...Is a hammer a pet?
metric = svd.get_ahat(('hammer', ('right', 'IsA', 'pet')))
print ''
print 'here is a measure of the likeleiood that a %s is a %s (high numbers show likelihood): %s' %('hammer', 'pet', str(metric))


#get rid of large objects we don't need
tensor = svd = None

#build a 2d analgy space
from csc.conceptnet4.analogyspace import conceptnet_2d_from_db
cnet = conceptnet_2d_from_db('en')
analogyspace = cnet.svd(k=50)

#test some conceptually similar and different things
cow = analogyspace.weighted_u['cow',:]
horse = analogyspace.weighted_u['horse',:]
pencil = analogyspace.weighted_u['pencil',:]
cowVersusHorse = cow.hat().dot(horse.hat())
pencilVerusHorse = pencil.hat().dot(horse.hat())
print ''
print 'on a normalized scale (%s to %s) %s is related to %s:  %s' %('-1.0', '+1.0', 'cow', 'horse', str(cowVersusHorse))
print ''
print 'on a normalized scale (%s to %s) %s is related to %s:  %s' %('-1.0', '+1.0', 'pencil', 'horse', str(pencilVerusHorse))

#find out what a pencil is related to; 
#get a normalized tensor and do pca; 
cnet_norm = conceptnet_2d_from_db('en').normalized()
analogyspace2 = cnet_norm.svd()
#get all dot products and pick best ones
pencil2 = analogyspace2.weighted_u['pencil', :]
pencil_like = analogyspace2.u_dotproducts_with(pencil2)
pencilTopItems = pencil_like.top_items()
print ''
print 'the things most closely related to %s are' %'pencil'
for p in pencilTopItems:
    print p

#we can also characterize things as e.g., "animal"
isAnimal = analogyspace.weighted_v[('right', u'IsA', u'animal'),:]
cowAnimal = cow.hat() * isAnimal.hat()
pencilAnimal = pencil.hat() * isAnimal.hat()
print ''
print 'numbers closer to 1 indicate %s is probably also %s: %s' %('cow', 'animal', str(cowAnimal))
  


'''
#here's how we can capture blog posts and contentn 'in the wild'
from csc.divisi import make_sparse_labeled_tensor
#we'll create a sparce, 2d tensor for out content
matrix = make_sparse_labeled_tensor(ndim=2)
#...open up a file    
from csc.nl import get_nl
en_nl = get_nl('en')
myfile = open('movieReviews.txt', 'r')
document = myfile.readlines()

#...and normalize its content
for line in document:
    for word in line.split():
        if en_nl.is_stopword(word): continue
        try:
            normalized = en_nl.normalize(word)
            matrix[normalized, document] += 1
        except:
            pass
        
#now we can do a pca
svd = matrix.svd(k=10)
#...and do the same sort of stuff
myword = 'scientist'
print myword
most_associated = svd.u_dotproducts_with(svd.weighted_u_vec(myword)).top_items(10)
print 'these words are most associated with %s' %myword
for m in most_associated:
    print m

pass
'''
