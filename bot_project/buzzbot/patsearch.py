import urllib
import simplejson

def PatSearch(searchString):

    query = urllib.urlencode({'q' : searchString})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' \
      % (query)
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    results = json['responseData']['results']
    for i in results:
        print i['title'] + ': ' + i['url']
        
if __name__ == '__main__':
    PatSearch('synovate')
