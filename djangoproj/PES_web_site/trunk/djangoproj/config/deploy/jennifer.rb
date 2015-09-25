# Deploy to jennifer from repo on moira

set :deploy_to, "/var/www/pes/"

###these settings deploy from moira's repo to moira as host
set :repository, "https://209.20.90.14/django/trunk/"
set :user, "buzzbot"
#set :host, "buzzbot@209.20.90.14"  #"moira"
set :host, "pat@0.0.0.0" #local
set :scm, :subversion

set :deploy_via, :checkout

role :app, host
role :web, host
role :db,  host, :primary => true

# Workaround for Capistrano bug when using SVN 
set :synchronous_connect, true
