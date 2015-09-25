# SUMMARY: This file deploys the application to servers.
#
# USAGE:
#   # Install Ruby, e.g., on Debian or Ubuntu:
#   sudo apt-get install ruby1.8 ruby1.8-dev libopenssl-ruby1.8
#
#   # Install Capistrano, e.g.:
#   sudo gem install capistrano
#
#   # See available tasks:
#   cap -T
#
#   # Run a task:
#   cap production deploy

set :application, "buzzbot"
set :group, "www-data"

# General options
ssh_options[:compression] = false
set :use_sudo, false
set :group_writable, true
set :keep_releases, 9

# Load multistage setting from config/deploy/*
#set :default_stage, 'production'
set :default_stage, 'moira'
set :stages,
  %w[
    moira
    production
    staging
    testing
    trunk
    jennifer
    dianne
  ]
begin
  require 'capistrano/ext/multistage'
rescue LoadError => e
  print <<-HERE
ERROR: Missing necessary library, install it with:
    sudo gem install capistrano-ext
  HERE
  exit 1
end

namespace :deploy do

  desc "Restart application"
  task :restart, :roles => :app do
    sudo "/usr/local/bin/apache2-force-reload"
  end

  desc "Start application"
  task :start, :roles => :app do
    sudo "/usr/local/bin/apache2-force-reload"
  end

  [:stop].each do |t|
    desc "Ignored by this setup."
    task t, :roles => :app do
      # Ignore
    end
  end

  desc "Ignored by this setup."
  task :migrate do
    # Ignore
  end

  desc "Add symlinks to shared content"
  task :symlink do
    run "ln -nsf #{latest_release} #{current_path}"
  end

  desc "Run after the update is finished"
  task :finalize_update, :except => { :no_release => true } do
    run "if test -f #{latest_release}/dev.cfg; then mv #{latest_release}/dev.cfg #{latest_release}/dev.cfg~; fi"
  end
end

#IK# after "deploy:update_code", "deploy:my_other_tasks"
