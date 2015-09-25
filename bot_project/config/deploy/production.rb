# Setup production environment

set :deploy_to, "/var/www/buzzbot"

set :repository, "https://svn.buzzbot.pragmaticraft.com/buzzbot_tubogears/branches/stable"
set :scm, :subversion

set :deploy_via, :checkout

set :user, "buzzbot"
set :host, "moira"
role :app, host
role :web, host
role :db,  host, :primary => true

# Workaround for Capistrano bug when using SVN 
set :synchronous_connect, true
