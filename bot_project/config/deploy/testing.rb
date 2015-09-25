# Setup testing environment

set :deploy_to, "/var/www/buzzbot"

set :repository, "ssh://hg@murad/buzzbot"
set :scm, :mercurial

set :deploy_via, :remote_cache

set :user, "buzzbot"
set :host, "buzzbot"
role :app, host
role :web, host
role :db,  host, :primary => true
