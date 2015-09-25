'''This routine imports text, creates a spase matrix from the words then analyzes the
associations
'''

from csc.divisi import make_sparse_labeled_tensor
from csc.nl import get_nl
en_nl = get_nl('en')


matrix = make_sparse_labeled_tensor(ndim=2)  #this is a matrix (num words X num words)
words = ['go', 'fly', 'a', 'kite', 'dogma', 'karma', 'fang', 'poodle', 'aussie', 'corgie', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
for w in words:
	if en_nl.is_stopword(w): 
		continue
	else:
		normalized = en_nl.normalize(w)
		matrix[normalized, w] += 1

'''Conduct a term frequency–inverse document frequency normalization on the catch (when we're getting material from
   documents); this keeps larger documents from dominating the analysis by counting factoring in the length of each
   document as well as the frequency with which words are used within them)
   '''
mat_normalized = matrix.normalized('tfidf')	#this does a term frequency–inverse document frequency (keeps large documents from dominating)
svd = mat_normalized.svd(k=10)
svd.summarize()

		
pass
