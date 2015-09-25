# Setup production environment, but use "trunk" instead of "stable"

eval File.read(File.join(File.dirname(__FILE__), "production.rb"))

set :repository, "https://svn.buzzbot.pragmaticraft.com/buzzbot_tubogears/trunk"
