# buzz_bot
web crawler / semantic classifier

(Working version).  Project to refactor (TurboGears -> Django) webapp designed to create sentiment scores 
related to companies, products, movies, etc.  Visit any number of URLs, follows links to any
depth, scrapes text around user-provided keywords.  The text is then analyzed using MIT's ConceptNet 
for conceptual proximity, then a simple classifier for positivity/negativity.
