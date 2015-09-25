# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=240)
    class Meta:
        db_table = u'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    message = models.TextField()
    class Meta:
        db_table = u'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    content_type_id = models.IntegerField()
    codename = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=90)
    first_name = models.CharField(max_length=90)
    last_name = models.CharField(max_length=90)
    email = models.CharField(max_length=225)
    password = models.CharField(max_length=384)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    group_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_user_permissions'

class BadUrlFragment(models.Model):
    id = models.IntegerField(primary_key=True)
    badstring = models.CharField(max_length=300, db_column='badString') # Field name made lowercase.
    reason = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'buzzapp_badUrlFragment'
        

class Search(models.Model):
    id = models.AutoField(primary_key=True)
    include = models.CharField(max_length=765, blank=True)
    exclude = models.CharField(max_length=765, blank=True)
    clearall = models.IntegerField(null=True, db_column='clearAll', blank=True) # Field name made lowercase.
    clearnonconform = models.IntegerField(null=True, db_column='clearNonconform', blank=True) # Field name made lowercase.
    viewcriteriaid = models.IntegerField(null=True, blank=True)
    andor = models.CharField(max_length=15, db_column='andOr', blank=True) # Field name made lowercase.
    deleteme = models.IntegerField(db_column='deleteMe') # Field name made lowercase.
    userid = models.IntegerField(null = True, blank=True)
    name = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'buzzapp_search'
        

class SearchViewcriteria(models.Model):
    id = models.AutoField(primary_key=True)
    searchid = models.ForeignKey(Search, db_column='searchid')
    include = models.CharField(max_length=765)
    exclude = models.CharField(max_length=765, blank=True)
    andor = models.CharField(max_length=30, db_column='andOr') # Field name made lowercase.
    isPublic= models.IntegerField(null=True, db_column= 'isPublic', blank=True)
    title=models.CharField(max_length=50, null=True, db_column='title', blank=True)
    class Meta:
        db_table = u'buzzapp_search_viewcriteria'        
        


class Url(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(unique=True, max_length=250)
    add_date = models.DateTimeField(null=True, blank=True)
    url_order = models.IntegerField(null=True, blank=True)
    delete_me = models.IntegerField(null=True, blank=True)
    visit_date = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=150, blank=True)
    readfailures = models.IntegerField(null=True, db_column='readFailures', blank=True) # Field name made lowercase.
    readsuccesses = models.IntegerField(null=True, db_column='readSuccesses', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'buzzapp_url'        

class Content(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(blank=True)
    dateacquired = models.DateTimeField(null=True, db_column='dateAcquired', blank=True) # Field name made lowercase.
    dateposted = models.DateTimeField(null=True, db_column='datePosted', blank=True) # Field name made lowercase.
    shortcont = models.CharField(unique=True, max_length=150, db_column='shortCont', blank=True) # Field name made lowercase.
    criteriaid = models.ForeignKey(SearchViewcriteria, null=True, db_column='criteriaid', blank=True)
    urlid = models.ForeignKey(Url, null=True, db_column='id', blank=True)

    class Meta:
        db_table = u'buzzapp_content'
        get_latest_by = 'dateposted'        
        
class ContentSearch(models.Model):
    id = models.AutoField(primary_key=True)
    searchid = models.ForeignKey(Search, db_column='searchid')
    contentid = models.ForeignKey(Content, db_column='contentid')
    urlid = models.ForeignKey(Url, db_column='urlid')
    class Meta:
        db_table = u'buzzapp_content_search'

class MetasearchSearch(models.Model):
    id = models.AutoField(primary_key=True)
    searchid = models.ForeignKey(Search, db_column='searchid')
    userid = models.IntegerField(null=True, blank=True, db_column ='userid')
    class Meta:
        db_table = u'buzzapp_metasearch_search'

class UrlHtml(models.Model):
    id = models.AutoField(primary_key=True)
    urlid = models.ForeignKey(Url, null=True, db_column='urlid', blank=True)
    html = models.TextField(blank=True)
    class Meta:
        db_table = u'buzzapp_url_html'

class UrlSearch(models.Model):
    id = models.AutoField(primary_key=True)
    urlid = models.ForeignKey(Url, null=True, db_column='urlid', blank=True)
    source = models.CharField(max_length=150, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    urlorder = models.IntegerField(null=True, blank=True)
    searchid = models.ForeignKey(Search, null=True, db_column='searchid', blank=True)
    class Meta:
        db_table = u'buzzapp_url_search'

class UrlTags(models.Model):
    id = models.AutoField(primary_key=True)
    urlid = models.ForeignKey(Url, db_column='urlid')
    name = models.CharField(max_length=150, blank=True)
    value = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'buzzapp_url_tags'
        
class PosWords(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    class Meta:
        db_table = u'buzzapp_poswords'    
        
class NegWords(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    class Meta:
        db_table = u'buzzapp_negwords'      
        
class NegationWords(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    class Meta:
        db_table = u'buzzapp_negationwords'         
        
class ObsceneWords(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=100)
    class Meta:
        db_table = u'buzzapp_obscenewords'            
        
class WordCount(models.Model):
    id = models.AutoField(primary_key=True)
    pos = models.IntegerField()
    neg = models.IntegerField()
    obscene = models.IntegerField()
    contentid = models.ForeignKey(Content, db_column='id')
    class Meta:
        db_table = u'buzzapp_wordcount' 
        
class ScoreMethods(models.Model):
    id = models.AutoField(primary_key=True)
    equation = models.CharField(max_length=100)
    class Meta:
        db_table = u'buzzapp_scoremethods'                 

class Scores(models.Model):
    id = models.AutoField(primary_key=True)
    methodid = models.ForeignKey(ScoreMethods, db_column='id')
    contentid = models.ForeignKey(Content, db_column='id')
    score = models.FloatField()
    class Meta:
        db_table = u'buzzapp_scores'     
        
        
class DjangoAdminLog(models.Model):
    id = models.AutoField(primary_key=True)
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField(null=True, blank=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=600)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = u'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    app_label = models.CharField(unique=True, max_length=250)
    model = models.CharField(unique=True, max_length=250)
    class Meta:
        db_table = u'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=120, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=300)
    name = models.CharField(max_length=150)
    class Meta:
        db_table = u'django_site'


