# Setup production environment on dianne

set :deploy_to, "/var/www/pes"

###these settings deploy from moira's repo to moira as host
set :repository, "https://209.20.90.14/django/trunk"
#set :repository, "http://svn.buzzbot.pragmaticraft.com/buzzbot_tubogears/branches/chart"
set :user, "buzzbot"
set :host, "buzzbot@209.20.90.14"  #"moira"

set :scm, :subversion

set :deploy_via, :checkout

role :app, host
role :web, host
role :db,  host, :primary => true

# Workaround for Capistrano bug when using SVN 
set :synchronous_connect, true
