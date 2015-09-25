from datetime import datetime
#set the database specifications here
dbUser = "buzzbot"
dbPass = "rootbak7"
dbSchema = "testdb"
dbHost = "localhost"

tableName_Url = "buzzapp_url"
tableName_Url_Tags= "buzzapp_url_tags"
tableName_Url_Search = "buzzapp_url_search"
tableName_Content = "buzzapp_content"
tableName_Content_Search ="buzzapp_content_search"
tableName_Content_Score = "buzzapp_content_score"
tableName_Search = "buzzapp_search"
tableName_Metasearch_Search = "buzzapp_metasearch_search"  #aggregate several searches under one metasearch
tableName_Url_Html = "buzzapp_url_html"
tableName_Search_Viewcriteria = "buzzapp_search_viewcriteria" #allows several parses of the content for the take (different than the key words used to search for urls)
tableName_BadUrlFragment = "buzzapp_badUrlFragment"
tableName_Negationwords= "buzzapp_negationwords"
tableName_Poswords = "buzzapp_poswords"
tableName_Negwords = "buzzapp_negwords"
tableName_Obscenewords = "buzzapp_obscenewords"
tableName_Scoremethods = "buzzapp_scoremethods"
tableName_Scores = "buzzapp_scores"
tableName_Wordcount = "buzzapp_wordcount"

##move these to the database
#set criteria for recording links found on visited web sites (make all lower case)
#mandatory words
linkInclude = ["blog"]
#exclusion words (# for bookmarks and = for submit/post buttons
linkExclude = ["2004", "2005", "2006", "2007", "#", "="]

#set the search keys here
bingSearchKey = "E8B19B3531DBA403B3B2E389C788ADEC59410105"

#set any general project values here
#return codes 
RETURN_SUCCESS = 0
RETURN_FAIL = -1
NULLDATE = datetime(1900,1,1)